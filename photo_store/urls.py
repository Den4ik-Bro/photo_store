from django.urls import path, include
from . import views

app_name = 'photo_store'

urlpatterns = [
    # path('', views.main, name='index'),
    path('', views.MainView.as_view(), name='index'),
    path('photographers/', views.photographers, name='photographers'),
    path('invite_to_orders/', views.invite_to_orders, name='invite_to_orders'),
    path('tag_photos/<int:tag_id>/', views.tag_photos, name='tag_photos'),
    path('profile/', views.profile_login, name='profile'),
    path('profile/<int:pk>/', include([
        path('', views.ProfileDetailView.as_view(), name='show_profile'),
        # path('edit/', views.edit_profile, name='edit_profile'),
        path('edit/', views.EditProfileView.as_view(), name='edit_profile'),

    ])),
    path('message/<int:conversationer_id>/', views.view_message, name='show_messages'),
    # path('orders/', views.orders, name='orders'),
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('create_order/', views.OrderCreateView.as_view(), name='create_order'),
    path('create_photo/', views.PhotoCreateView.as_view(), name='create_photo'),
    path('order/<int:order_id>/', include([
        path('', views.get_order, name='order'),
        path('edit/', views.edit_order, name='edit_order'),
    ])),
    path('ok/', views.OkView.as_view(), name='response sent'),
    path('select_response/<int:response_id>/', views.select_response, name='select_response'),
    path('photo_view/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_view'),
    path('del_photo/<int:pk>/', views.DeletePhotoView.as_view(), name='del_photo'),
    path('del_order/<int:order_id>/', views.del_order, name='del_order'),
]

