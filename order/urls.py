from django.urls import path, include
from . import views


app_name = 'order'

urlpatterns = [
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('create_order/', views.OrderCreateView.as_view(), name='create_order'),
    path('order/<int:pk>/', views.GetOrderDetailView.as_view(), name='order'),
    path('del_order/<int:pk>/', views.DeleteOrderView.as_view(), name='del_order'),
    path('edit_order/<int:pk>/', views.EditOrderUpdateView.as_view(), name='edit_order'),
    path('invite_to_orders/', views.InviteToOrders.as_view(), name='invite_to_orders'),
    path('ok/', views.OkView.as_view(), name='response sent'),  # пока пусть будет :)
    path('select_response/<int:pk>/', views.SelectResponseView.as_view(), name='select_response'),
    path('create_response/<int:pk>', views.CreateResponse.as_view(), name='create_response'),
    path('create_rate_response/<int:pk>', views.CreateRateResponse.as_view(), name='create_rate_response'),
]