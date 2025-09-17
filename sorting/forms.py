from django import forms
from .models import Socket, BagType, BagSubtype


class SocketSelectionForm(forms.Form):
    socket = forms.ModelChoiceField(
        queryset=Socket.objects.filter(is_active=True).order_by('order'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Wybierz gniazdo..."
    )
    bag_source = forms.ChoiceField(
        choices=[('IN', 'IN'), ('OUT', 'OUT')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class BagTypeSelectionForm(forms.Form):
    def __init__(self, socket_id=None, bag_source=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if socket_id:
            queryset = BagType.objects.filter(socket_id=socket_id, is_active=True)
            
            # Filter by bag_source if provided (for SEP socket)
            if bag_source:
                queryset = queryset.filter(bag_source=bag_source)
            
            self.fields['bag_type'] = forms.ModelChoiceField(
                queryset=queryset.order_by('order'),
                widget=forms.Select(attrs={'class': 'form-control'}),
                empty_label="Wybierz typ worka..."
            )
        else:
            self.fields['bag_type'] = forms.ModelChoiceField(
                queryset=BagType.objects.none(),
                widget=forms.Select(attrs={'class': 'form-control'}),
                empty_label="Najpierw wybierz gniazdo..."
            )
    
    parameter = forms.ChoiceField(
        choices=[('Standard', 'Standard'), ('Extra', 'Extra')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class BagSubtypeSelectionForm(forms.Form):
    def __init__(self, bag_type_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if bag_type_id:
            queryset = BagSubtype.objects.filter(bag_type_id=bag_type_id, is_active=True)
            
            self.fields['bag_subtype'] = forms.ModelChoiceField(
                queryset=queryset.order_by('order'),
                widget=forms.Select(attrs={'class': 'form-control'}),
                empty_label="Wybierz podtyp..."
            )
        else:
            self.fields['bag_subtype'] = forms.ModelChoiceField(
                queryset=BagSubtype.objects.none(),
                widget=forms.Select(attrs={'class': 'form-control'}),
                empty_label="Najpierw wybierz typ worka..."
            )


class WeightForm(forms.Form):
    weight_kg = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'inputmode': 'decimal',
            'pattern': '[0-9]*\.?[0-9]*',
            'autocomplete': 'off',
            'placeholder': '0,00'
        }),
        label="Waga (kg)"
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Opcjonalne notatki...'
        }),
        label="Notatki"
    )


