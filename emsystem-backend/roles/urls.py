from django.urls import path
from . import views

urlpatterns = [
    path('permissions', views.permission_list,name="permission_list"),
    # path('roles',views.role_list,name="role_list"),
    # path('roles',views.role_create,name="role_create"),
    
    # List roles and create roles
    path("roles", views.roles_api, name="roles_api"),
    # path("roles/<int:role_id>",views.role_detail,name="role_detail"),
    # Retrieve role details or delete a role
    # Roles details and delete roles
    path("roles/<int:role_id>",views.role_detail_api,name="role_detail_api"),
    path("roles/<int:role_id>/update",views.role_update,name="role_update"),
]
