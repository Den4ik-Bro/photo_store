from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as token_views
from . import views

router = DefaultRouter()
router.register('orders', viewset=views.OrderApiViewSet, basename='orders')
router.register('users', viewset=views.UserViewSet, basename='users')
router.register('messages', viewset=views.MessageViewSet, basename='messages')
router.register('responses', viewset=views.ResponseViewSet, basename='responses')
router.register('photos', viewset=views.PhotoViewSet, basename='photos')
router.register('topics', viewset=views.TopicViewSet, basename='topics')
router.register('user_photos', viewset=views.UserPhotoApiViewSet, basename='user_photos')
router.register('user_response_photos', viewset=views.UserResponsePhotoApiViewSet, basename='user_response_photos')
router.register('user_orders', viewset=views.UserOrderApiViewSet, basename='user_orders')
router.register('user_messages', viewset=views.UserMessagesApiViewSet, basename='user_messages')
router.register('user_responses', viewset=views.UserResponseApiViewSet, basename='user_responses')


app_name = 'api_store'


urlpatterns = [
    path('api-token-auth/', token_views.obtain_auth_token),
    path('', include(router.urls)),
    # ниже пока тестовые урлы, пока не удаляю
    path('show_order_api/<int:pk>/', views.show_order_ajax, name='show_order_ajax'),
    path('create_order_api/', views.create_or_update_order_api, name='create_order_api'),
    path('update_order_api/<int:pk>', views.create_or_update_order_api, name='create_or_update_order_api'),
    path('order_list_api/', views.show_order_ist_api),
    path('create_message_api/', views.create_message_api, name='create_message_api'),
    path('show_photo_api/<int:pk>/', views.show_photo_ajax, name='show_photo_api'),
    path('create_photo_api/', views.create_photo_api, name='create_photo_api'),

    path('test_ajax/', views.test_ajax),
    path('test_create_ajax/', views.create_ajax, name='create_order_ajax'),
    path('test_create_response_ajax/<int:order_id>/', views.create_response_ajax, name='create_response_ajax'),
    path('test_create_message_ajax/<int:pk>/', views.create_message_ajax, name='create_message_ajax'),
    path('test_show_message_ajax/<int:pk>/', views.show_message_ajax, name='show_message_ajax'),
    # path('api_store/orders/', views.ApiOrderListView.as_view(), name='api_orders'),
    # path('api_store/orders/<int:pk>/', views.ApiOrderDetailView.as_view(), name='api_order')
    # path('api_store/orders/<int:pk>/', views.ApiListUpdateOrderView.as_view(), name='api_list_update_order'),
    # path('api_store/orders/', views.ApiListUpdateOrderView.as_view(), name='api_list_order'),
]
