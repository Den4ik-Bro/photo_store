from django.urls import path, include
from . import views

app_name = 'photo_store'

urlpatterns = [
    path('', views.main, name='index'),
    path('photographers/', views.photographers, name='photographers'),
    path('invite_to_order/<int:user_id>/', views.invite_to_order, name='invite_to_order'),
    path('tag_photos/<int:tag_id>/', views.tag_photos),
    path('profile/', views.profile_login),
    path('profile/<int:user_id>/', include([
        path('', views.profile, name='show_profile'),
        path('edit/', views.edit_profile),

    ])),
    path('message/<int:conversationer_id>/', views.view_message, name='show_messages'),
    path('orders/', views.orders),
    path('order/<int:order_id>/', include([
        path('', views.get_order),
        path('edit/', views.edit_order),
    ])),
    path('ok/', views.ok, name='response sent'),
    path('select_response/<int:response_id>/', views.select_response),
    path('photo_view/<int:photo_id>/', views.photo_view),
    path('del_photo/<int:photo_id>/', views.del_photo),
    path('del_order/<int:order_id>/', views.del_order),
]

