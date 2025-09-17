from django.urls import path
from . import views

app_name = 'sorting'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('sockets/', views.SocketListView.as_view(), name='socket_list'),
    path('sockets/<int:socket_id>/', views.SocketDetailView.as_view(), name='socket_detail'),
    path('bags/', views.BagListView.as_view(), name='bag_list'),
    path('bags/<int:bag_id>/', views.BagDetailView.as_view(), name='bag_detail'),
    path('personnel/', views.PersonnelListView.as_view(), name='personnel_list'),
    path('sorted-bags/', views.SortedBagListView.as_view(), name='sorted_bag_list'),
    
    # Multi-step bag creation form URLs
    path('add-bag/step1/', views.Step1SocketSelectionView.as_view(), name='step1_socket_selection'),
    path('add-bag/step2/', views.Step2BagTypeSelectionView.as_view(), name='step2_bagtype_selection'),
    path('add-bag/step2b/', views.Step2bSubtypeSelectionView.as_view(), name='step2b_subtype_selection'),
    path('add-bag/step3/', views.Step3WeightEntryView.as_view(), name='step3_weight_entry'),
    path('add-bag/step4/', views.Step4SummaryView.as_view(), name='step4_summary'),
    path('add-bag/continue/', views.ContinueOrFinishView.as_view(), name='continue_or_finish'),
    
    # Settings URLs
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/update-order/', views.UpdateOrderView.as_view(), name='update_order'),
]