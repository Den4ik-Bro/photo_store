from django.urls import path
from . import views


app_name = 'message'

urlpatterns = [
    path('message/<int:pk>/', views.ViewMessage.as_view(), name='show_messages'),
    path('create_message/<int:user_id>/', views.CreateMessage.as_view(), name='create_message'),
]

