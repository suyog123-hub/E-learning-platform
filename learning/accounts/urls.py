from django.urls import path
from .views import  *

urlpatterns = [
     path('signin/', signin, name='signin'),
     path('register/',register, name='register'),
     path('profile/', profile, name='profile'),
     path('logout/', signout, name='logout'),
    path('renew_password/', renew_password, name='renew_password'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('cart/add/<int:id>/', cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/', item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/', item_decrement, name='item_decrement'),
    path('cart/cart_clear/', cart_clear, name='cart_clear'),
    path('cart/cart-detail/', cart_detail, name='cart_detail'),

    path('favorites/add/<int:course_id>/', add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:course_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', favorites_list, name='favorite_courses'),
    


]