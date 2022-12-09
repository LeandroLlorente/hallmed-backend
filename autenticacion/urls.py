from django.urls import path
from .endpoints.auth import login, logout, \
    add_user, change_password, delete_user, roles_view, list_users, update_user, update_user_by_id

urlpatterns = [
    path('api/v1/auth/login', login),
    path('api/v1/auth/logout', logout),
    path('api/v1/auth/all', list_users),
    path('api/v1/auth/register', add_user),
    path('api/v1/auth/password', change_password),
    path('api/v1/auth/delete', delete_user),
    path('api/v1/auth/update', update_user),
    path('api/v1/auth/roles', roles_view),
    path('api/v1/auth/updateid', update_user_by_id),

]