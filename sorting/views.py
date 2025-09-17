from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.db.models import Count, Q
from django.core.serializers.json import DjangoJSONEncoder
from .models import Socket, Bag, SortedBag, SortingPerson, BagType, BagSubtype
from .forms import SocketSelectionForm, BagTypeSelectionForm, BagSubtypeSelectionForm, WeightForm
import uuid
import json


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'sorting/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_sockets': Socket.objects.filter(is_active=True).count(),
            'total_bags': Bag.objects.count(),
            'processed_bags': Bag.objects.filter(is_processed=True).count(),
            'pending_bags': Bag.objects.filter(is_processed=False).count(),
            'sorted_bags': SortedBag.objects.count(),
            'active_personnel': SortingPerson.objects.all().count(),
        })
        return context


class SocketListView(LoginRequiredMixin, ListView):
    model = Socket
    template_name = 'sorting/socket_list.html'
    context_object_name = 'sockets'

    def get_queryset(self):
        return Socket.objects.annotate(
            bag_count=Count('bags')
        ).order_by('socket_id')


class SocketDetailView(LoginRequiredMixin, DetailView):
    model = Socket
    template_name = 'sorting/socket_detail.html'
    pk_url_kwarg = 'socket_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bags'] = self.object.bags.all().order_by('-received_at')
        return context


class BagListView(LoginRequiredMixin, ListView):
    model = Bag
    template_name = 'sorting/bag_list.html'
    context_object_name = 'bags'

    def get_queryset(self):
        bags = Bag.objects.select_related('socket', 'sorting_person', 'bag_type').order_by('-received_at')
        
        status_filter = self.request.GET.get('status')
        if status_filter == 'processed':
            bags = bags.filter(is_processed=True)
        elif status_filter == 'pending':
            bags = bags.filter(is_processed=False)
        
        bag_type = self.request.GET.get('bag_type')
        if bag_type:
            bags = bags.filter(bag_type=bag_type)
        
        return bags

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'bag_types': BagType.objects.all(),
            'current_filters': {
                'status': self.request.GET.get('status'),
                'bag_type': self.request.GET.get('bag_type'),
            }
        })
        return context


class BagDetailView(LoginRequiredMixin, DetailView):
    model = Bag
    template_name = 'sorting/bag_detail.html'
    pk_url_kwarg = 'bag_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sorted_bag'] = getattr(self.object, 'sorted_bag', None)
        return context


class PersonnelListView(LoginRequiredMixin, ListView):
    model = SortingPerson
    template_name = 'sorting/personnel_list.html'
    context_object_name = 'personnel'

    def get_queryset(self):
        return SortingPerson.objects.annotate(
            bags_sorted=Count('sorted_bags')
        ).order_by('name')


class SortedBagListView(LoginRequiredMixin, ListView):
    model = SortedBag
    template_name = 'sorting/sorted_bag_list.html'
    context_object_name = 'sorted_bags'

    def get_queryset(self):
        sorted_bags = SortedBag.objects.select_related('original_bag').order_by('-created_at')
        
        destination_filter = self.request.GET.get('destination')
        if destination_filter:
            sorted_bags = sorted_bags.filter(destination=destination_filter)
        
        status_filter = self.request.GET.get('status')
        if status_filter:
            sorted_bags = sorted_bags.filter(status=status_filter)
        
        return sorted_bags

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'destinations': SortedBag.DESTINATION_CHOICES,
            'statuses': SortedBag.STATUS_CHOICES,
            'current_filters': {
                'destination': self.request.GET.get('destination'),
                'status': self.request.GET.get('status'),
            }
        })
        return context


# Multi-step bag creation form views

class Step1SocketSelectionView(LoginRequiredMixin, FormView):
    template_name = 'sorting/bag_form_step1.html'
    form_class = SocketSelectionForm
    success_url = reverse_lazy('sorting:step2_bagtype_selection')

    def form_valid(self, form):
        socket = form.cleaned_data['socket']
        bag_source = form.cleaned_data.get('bag_source')
        
        session_data = {
            'socket_id': socket.id,
            'socket_name': socket.socket_name
        }
        
        # Add bag_source if it's provided (for SEP socket)
        if bag_source:
            session_data['bag_source'] = bag_source
        
        self.request.session['bag_form_data'] = session_data
        self.request.session.modified = True
        return super().form_valid(form)


class Step2BagTypeSelectionView(LoginRequiredMixin, View):
    template_name = 'sorting/bag_form_step2.html'

    def dispatch(self, request, *args, **kwargs):
        if 'bag_form_data' not in request.session:
            messages.error(request, 'Please start from step 1.')
            return redirect('sorting:step1_socket_selection')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        socket_id = request.session['bag_form_data']['socket_id']
        bag_source = request.session['bag_form_data'].get('bag_source')
        form = BagTypeSelectionForm(socket_id=socket_id, bag_source=bag_source)
        return render(request, self.template_name, self.get_context_data(form=form))

    def post(self, request):
        socket_id = request.session['bag_form_data']['socket_id']
        bag_source = request.session['bag_form_data'].get('bag_source')
        form = BagTypeSelectionForm(socket_id=socket_id, bag_source=bag_source, data=request.POST)
        
        if form.is_valid():
            bag_type = form.cleaned_data['bag_type']
            parameter = form.cleaned_data.get('parameter')
            
            session_update = {
                'bag_type_id': bag_type.id,
                'bag_type_name': bag_type.name
            }
            
            # Add parameter if it was selected
            if parameter:
                session_update['parameter'] = parameter
                session_update['bag_type_display'] = f"{bag_type.name} ({parameter})"
            else:
                session_update['bag_type_display'] = bag_type.name
            
            request.session['bag_form_data'].update(session_update)
            request.session.modified = True
            
            # Check if this bag type has subtypes
            if bag_type.subtypes.filter(is_active=True).exists():
                return redirect('sorting:step2b_subtype_selection')
            else:
                return redirect('sorting:step3_weight_entry')
        
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_context_data(self, form):
        socket_name = self.request.session['bag_form_data']['socket_name']
        bag_source = self.request.session['bag_form_data'].get('bag_source')
        
        # Get bag type parameters for JavaScript
        bag_type_parameters = {}
        for bag_type in form.fields['bag_type'].queryset:
            if bag_type.parameter and isinstance(bag_type.parameter, list) and len(bag_type.parameter) > 1:
                # Check if it has both Standard and Extra
                if 'Standard' in bag_type.parameter and 'Extra' in bag_type.parameter:
                    bag_type_parameters[bag_type.id] = bag_type.parameter
        
        context = {
            'form': form,
            'socket_name': socket_name,
            'bag_type_parameters_json': json.dumps(bag_type_parameters)
        }
        
        # Add bag_source to context if it exists (for SEP socket)
        if bag_source:
            context['bag_source'] = bag_source
            context['socket_info'] = f"{socket_name} ({bag_source})"
        else:
            context['socket_info'] = socket_name
        
        return context


class Step2bSubtypeSelectionView(LoginRequiredMixin, View):
    template_name = 'sorting/bag_form_step2b.html'

    def dispatch(self, request, *args, **kwargs):
        if 'bag_form_data' not in request.session or 'bag_type_id' not in request.session['bag_form_data']:
            messages.error(request, 'Please complete previous steps first.')
            return redirect('sorting:step1_socket_selection')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        bag_type_id = request.session['bag_form_data']['bag_type_id']
        form = BagSubtypeSelectionForm(bag_type_id=bag_type_id)
        return render(request, self.template_name, self.get_context_data(form=form))

    def post(self, request):
        bag_type_id = request.session['bag_form_data']['bag_type_id']
        form = BagSubtypeSelectionForm(bag_type_id=bag_type_id, data=request.POST)
        
        if form.is_valid():
            bag_subtype = form.cleaned_data['bag_subtype']
            
            # Update session with subtype information
            request.session['bag_form_data'].update({
                'bag_subtype_id': bag_subtype.id,
                'bag_subtype_name': bag_subtype.name
            })
            
            # Update bag_type_display to include subtype
            bag_type_name = request.session['bag_form_data']['bag_type_name']
            parameter = request.session['bag_form_data'].get('parameter')
            
            if parameter:
                display_name = f"{bag_type_name} - {bag_subtype.name} ({parameter})"
            else:
                display_name = f"{bag_type_name} - {bag_subtype.name}"
            
            request.session['bag_form_data']['bag_type_display'] = display_name
            request.session.modified = True
            return redirect('sorting:step3_weight_entry')
        
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_context_data(self, form):
        socket_name = self.request.session['bag_form_data']['socket_name']
        bag_type_name = self.request.session['bag_form_data']['bag_type_name']
        bag_source = self.request.session['bag_form_data'].get('bag_source')
        
        if bag_source:
            socket_info = f"{socket_name} ({bag_source})"
        else:
            socket_info = socket_name
        
        return {
            'form': form,
            'socket_info': socket_info,
            'bag_type_name': bag_type_name
        }


class Step3WeightEntryView(LoginRequiredMixin, View):
    template_name = 'sorting/bag_form_step3.html'

    def dispatch(self, request, *args, **kwargs):
        if 'bag_form_data' not in request.session or 'bag_type_id' not in request.session['bag_form_data']:
            messages.error(request, 'Please complete previous steps first.')
            return redirect('sorting:step1_socket_selection')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = WeightForm()
        return render(request, self.template_name, self.get_context_data(form=form))

    def post(self, request):
        form = WeightForm(request.POST)
        if form.is_valid():
            weight_kg = form.cleaned_data['weight_kg']
            notes = form.cleaned_data['notes']
            request.session['bag_form_data'].update({
                'weight_kg': str(weight_kg),
                'notes': notes
            })
            request.session.modified = True
            return redirect('sorting:step4_summary')
        
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_context_data(self, form):
        bag_type_display = self.request.session['bag_form_data'].get(
            'bag_type_display', 
            self.request.session['bag_form_data']['bag_type_name']
        )
        socket_name = self.request.session['bag_form_data']['socket_name']
        bag_source = self.request.session['bag_form_data'].get('bag_source')
        
        # Create socket_info with bag_source if it exists
        if bag_source:
            socket_info = f"{socket_name} ({bag_source})"
        else:
            socket_info = socket_name
        
        return {
            'form': form,
            'bag_type_name': bag_type_display,
            'socket_name': socket_name,
            'socket_info': socket_info
        }


class Step4SummaryView(LoginRequiredMixin, View):
    template_name = 'sorting/bag_form_step4.html'
    continue_template = 'sorting/bag_form_continue.html'

    def dispatch(self, request, *args, **kwargs):
        if 'bag_form_data' not in request.session or 'weight_kg' not in request.session['bag_form_data']:
            messages.error(request, 'Please complete previous steps first.')
            return redirect('sorting:step1_socket_selection')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request):
        form_data = request.session['bag_form_data']
        
        # Create the bag entry
        socket = Socket.objects.get(id=form_data['socket_id'])
        bag_type = BagType.objects.get(id=form_data['bag_type_id'])
        
        # Get subtype if it exists
        bag_subtype = None
        if 'bag_subtype_id' in form_data:
            bag_subtype = BagSubtype.objects.get(id=form_data['bag_subtype_id'])
        
        # Generate unique bag ID
        bag_id = f"BAG_{uuid.uuid4().hex[:8].upper()}"
        
        # Check if Extra parameter was selected
        extra = form_data.get('parameter') == 'Extra'
        
        bag = Bag.objects.create(
            bag_id=bag_id,
            socket=socket,
            bag_type=bag_type,
            bag_subtype=bag_subtype,
            weight_kg=form_data['weight_kg'],
            notes=form_data['notes'],
            item_count=1,  # Default to 1 for now
            extra=extra
        )
        
        # Ask if user wants to add another bag
        return render(request, self.continue_template, {
            'bag': bag,
            'socket_name': form_data['socket_name']
        })

    def get_context_data(self):
        form_data = self.request.session['bag_form_data']
        
        # Add socket_info and bag_type_display for display purposes
        bag_source = form_data.get('bag_source')
        if bag_source:
            socket_info = f"{form_data['socket_name']} ({bag_source})"
        else:
            socket_info = form_data['socket_name']
        
        # Get bag type display name (with parameter if available)
        bag_type_display = form_data.get('bag_type_display', form_data['bag_type_name'])
        
        # Create enhanced form_data with socket_info and bag_type_display
        enhanced_form_data = dict(form_data)
        enhanced_form_data['socket_info'] = socket_info
        enhanced_form_data['bag_type_display'] = bag_type_display
        
        return {
            'form_data': enhanced_form_data
        }


class ContinueOrFinishView(LoginRequiredMixin, View):
    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'continue_same_socket':
            # Keep socket, go to step 2
            if 'bag_form_data' in request.session:
                # Remove bag-specific data but keep socket
                socket_data = {
                    'socket_id': request.session['bag_form_data']['socket_id'],
                    'socket_name': request.session['bag_form_data']['socket_name']
                }
                if 'bag_source' in request.session['bag_form_data']:
                    socket_data['bag_source'] = request.session['bag_form_data']['bag_source']
                request.session['bag_form_data'] = socket_data
            return redirect('sorting:step2_bagtype_selection')
        
        elif action == 'continue_new_socket':
            # Clear all data, start fresh
            if 'bag_form_data' in request.session:
                del request.session['bag_form_data']
            return redirect('sorting:step1_socket_selection')
        
        else:  # finish
            # Clear session data
            if 'bag_form_data' in request.session:
                del request.session['bag_form_data']
            messages.info(request, 'Bag entry process completed.')
            return redirect('sorting:bag_list')
    
    def get(self, request):
        return redirect('sorting:step1_socket_selection')


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'sorting/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sockets': Socket.objects.filter(is_active=True).order_by('order', 'socket_id'),
            'bag_types': BagType.objects.filter(is_active=True).order_by('order', 'name'),
            'bag_subtypes': BagSubtype.objects.filter(is_active=True).order_by('bag_type__name', 'order', 'name'),
        })
        return context


class UpdateOrderView(LoginRequiredMixin, View):
    def post(self, request):
        model_type = request.POST.get('model_type')
        order_data = request.POST.getlist('order[]')
        
        if model_type == 'socket':
            self._update_socket_order(order_data)
        elif model_type == 'bagtype':
            self._update_bagtype_order(order_data)
        elif model_type == 'bagsubtype':
            self._update_bagsubtype_order(order_data)
        
        messages.success(request, f'{model_type.title()} order updated successfully!')
        return redirect('sorting:settings')
    
    def _update_socket_order(self, order_data):
        for index, socket_id in enumerate(order_data, 1):
            Socket.objects.filter(id=socket_id).update(order=index)
    
    def _update_bagtype_order(self, order_data):
        for index, bagtype_id in enumerate(order_data, 1):
            BagType.objects.filter(id=bagtype_id).update(order=index)
    
    def _update_bagsubtype_order(self, order_data):
        for index, subtype_id in enumerate(order_data, 1):
            BagSubtype.objects.filter(id=subtype_id).update(order=index)
