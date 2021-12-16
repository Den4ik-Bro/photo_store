from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as token_views

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


app_name = 'photo_store'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('photographers/', views.PhotographersListView.as_view(), name='photographers'),
    path('invite_to_orders/', views.InviteToOrders.as_view(), name='invite_to_orders'),
    path('tag_photos/<int:pk>/', views.TagPhotoDetailView.as_view(), name='tag_photos'),
    path('profile/', views.profile_login, name='profile'),
    path('profile/<int:pk>/', include([
        path('', views.ProfileDetailView.as_view(), name='show_profile'),
        path('edit/', views.EditProfileView.as_view(), name='edit_profile'),
    ])),
    path('message/<int:pk>/', views.ViewMessage.as_view(), name='show_messages'),
    path('create_message/<int:user_id>/', views.CreateMessage.as_view(), name='create_message'),
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('create_order/', views.OrderCreateView.as_view(), name='create_order'),
    path('create_photo/', views.PhotoCreateView.as_view(), name='create_photo'),
    path('order/<int:pk>/', include([
        path('', views.GetOrderDetailView.as_view(), name='order')
    ])),
    path('ok/', views.OkView.as_view(), name='response sent'),
    path('select_response/<int:pk>/', views.SelectResponseView.as_view(), name='select_response'),
    path('create_response/<int:pk>', views.CreateResponse.as_view(), name='create_response'),
    path('create_response_photo/<int:pk>', views.CreateResponsePhoto.as_view(), name='create_response_photo'),
    path('create_rate_response/<int:pk>', views.CreateRateResponse.as_view(), name='create_rate_response'),
    path('photo_view/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_view'),
    path('create_tag/<int:photo_id>/', views.TagCreateView.as_view(), name='create_tag'),
    path('del_photo/<int:pk>/', views.DeletePhotoView.as_view(), name='del_photo'),
    path('del_order/<int:pk>/', views.DeleteOrderView.as_view(), name='del_order'),
    path('edit_order/<int:pk>/', views.EditOrderUpdateView.as_view(), name='edit_order'),
    # path('test_message/<int:pk>/', views.TestMessage.as_view(), name='test_message'),

  # API...
    path('api/', include([
        path('api-token-auth/', token_views.obtain_auth_token)
    ])),
    path('api/', include(router.urls)),
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
    # path('api/orders/', views.ApiOrderListView.as_view(), name='api_orders'),
    # path('api/orders/<int:pk>/', views.ApiOrderDetailView.as_view(), name='api_order')
    # path('api/orders/<int:pk>/', views.ApiListUpdateOrderView.as_view(), name='api_list_update_order'),
    # path('api/orders/', views.ApiListUpdateOrderView.as_view(), name='api_list_order'),


]

