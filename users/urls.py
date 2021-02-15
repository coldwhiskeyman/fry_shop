from django.urls import path

from users.views import (
    DepositView,
    UserCreateView,
    UserDetailView,
    UserLoginView,
    UserLogoutView
)


urlpatterns = [
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', UserLogoutView.as_view(), name='logout'),
    path('register', UserCreateView.as_view(), name='user_create'),
    path('<int:pk>', UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/deposit', DepositView.as_view(), name='deposit'),
]
