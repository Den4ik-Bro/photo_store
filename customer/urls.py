from django.urls import path, include
from . import views


app_name = 'customer'

urlpatterns =[
    path('profile/', views.profile_login, name='profile'),
    path('profile/<int:pk>/', include([
        path('', views.ProfileDetailView.as_view(), name='show_profile'),
        path('edit/', views.EditProfileView.as_view(), name='edit_profile'),
        path('edit_avatar/', views.EditProfileImageView.as_view(), name='edit_avatar')
    ])),
    path('register/', views.RegistrationFormView.as_view()),
    path('create_user/', views.UserCreateView.as_view()),
    path('photographers/', views.PhotographersListView.as_view(), name='photographers'),
]