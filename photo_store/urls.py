from django.urls import path
from . import views


app_name = 'photo_store'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('tag_photos/<int:pk>/', views.TagPhotoDetailView.as_view(), name='tag_photos'),
    path('create_photo/', views.PhotoCreateView.as_view(), name='create_photo'),
    path('create_response_photo/<int:pk>', views.CreateResponsePhoto.as_view(), name='create_response_photo'),
    path('photo_view/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_view'),
    path('create_tag/<int:photo_id>/', views.TagCreateView.as_view(), name='create_tag'),
    path('del_photo/<int:pk>/', views.DeletePhotoView.as_view(), name='del_photo'),
]

