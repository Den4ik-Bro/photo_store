from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.main),
    path('tag_photos/<int:tag_id>/', views.tag_photos),
    path('profile/', views.profile_login),
    path('profile/<int:user_id>/', include([
        path('', views.profile),
        path('edit/', views.edit_profile),
    ])),
    path('orders/', views.orders),
    path('order/<int:order_id>/', include([
        path('', views.get_order),
        path('edit/', views.edit_order),
    ])),
    path('ok/', views.ok),
    path('select_response/<int:response_id>/', views.selected_response),
    path('photo_view/<int:photo_id>/', views.photo_view),
    path('del_photo/<int:photo_id>/', views.del_photo),
    path('del_order/<int:order_id>/', views.del_order)
]

