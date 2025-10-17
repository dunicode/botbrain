from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.HistoryCreateView.as_view(), name='history-create'),
    path('history/list/', views.HistoryListView.as_view(), name='history-list'),
    path('history/<int:pk>/', views.HistoryDetailView.as_view(), name='history-detail'),
    path('commands/list/', views.CommandListView.as_view(), name='command-list'),
    path('raspberries/list/', views.RaspberryListView.as_view(), name='raspberry-list'),
    path('raspberries/<slug:raspberry_slug>/get-command/', views.PendingCommandView.as_view(), name='get-pending-commands'),
    path('raspberries/<slug:raspberry_slug>/ack-command/', views.AckCommandView.as_view(), name='ack-command'),
]