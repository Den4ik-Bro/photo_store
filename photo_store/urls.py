from django.urls import path, include
from . import views

app_name = 'photo_store'

urlpatterns = [
    path('', views.main, name='index'),
    path('photographers/', views.photographers, name='photographers'),
    path('invite_to_orders/', views.invite_to_orders, name='invite_to_orders'),
    path('tag_photos/<int:tag_id>/', views.tag_photos, name='tag_photos'),
    path('profile/', views.profile_login, name='profile'),
    path('profile/<int:user_id>/', include([
        path('', views.profile, name='show_profile'),
        path('edit/', views.edit_profile, name='edit_profile'),

    ])),
    path('message/<int:conversationer_id>/', views.view_message, name='show_messages'),
    path('orders/', views.orders, name='orders'),
    path('order/<int:order_id>/', include([
        path('', views.get_order, name='order'),
        path('edit/', views.edit_order, name='edit_order'),
    ])),
    path('ok/', views.ok, name='response sent'),
    path('select_response/<int:response_id>/', views.select_response, name='select_response'),
    path('photo_view/<int:photo_id>/', views.photo_view, name='photo_view'),
    path('del_photo/<int:photo_id>/', views.del_photo, name='del_photo'),
    path('del_order/<int:order_id>/', views.del_order, name='del_order'),
]

