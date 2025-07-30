from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from fourlabs_auth.views import (RequestEmailView, VerifyCodeView, ChangePasswordView, DeleteAccountView, ExportUserDataView,
                         EditUserNameView)

urlpatterns = [
    path('login/', RequestEmailView.as_view(), name='login'),
    path('verify/', VerifyCodeView.as_view(), name='verify_code'),
    path('edit-user-name/', EditUserNameView.as_view(), name='edit-user-name'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('export-user-data/', ExportUserDataView.as_view(), name='export-user-data'),
    path('logout/', LogoutView.as_view(next_page='login', http_method_names=['get', 'post']), name='logout'),
]
