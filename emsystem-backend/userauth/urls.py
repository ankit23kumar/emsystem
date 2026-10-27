from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name= 'home'),
    path('user-list',views.user_list, name = 'user_list'),
    path('register',views.register_user, name = 'register_user'),
    path('login',views.login_user,name= 'login_user'),
    path('user-create', views.create_user, name='create_user'),
    path('update/<int:user_id>',views.update_user,name='update_user'),
    path('delete/<int:user_id>',views.delete_user,name='delete_user'),
    # path("renew-account/<int:user_id>",views.renew_account,name="renew_account"),
    # path("reactivate-account",views.reactivate_account,name="reactivate_account"),
    path('me',views.my_profile,name='my_profile'),
    path('password-reset',views.reset_password,name= 'reset_password')
]
