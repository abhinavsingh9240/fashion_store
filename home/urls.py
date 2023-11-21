from django.urls import path

from home.views import settings_views, all_views

urlpatterns = [
    path('', all_views.index, name='index'),
    path('list', all_views.list_view, name="list"),
    path('product/<int:product_id>', all_views.product_view, name="product"),
    path('signin', all_views.signin_view, name="sign_in"),
    path('signup', all_views.signup_view, name="sign_up"),
    path('signout', all_views.signout_view, name="sign_out"),
    path('cart_panel/',all_views.cart_panel,name='cart_panel'),
    path('search/',all_views.search_view,name='search'),
    path('checkout/',all_views.checkout_view,name='checkout'),
    path('payment/',all_views.payment_view,name="payment"),
    path('paymenthandler/', all_views.paymenthandler, name='paymenthandler'),
    # settings
    path('settings', settings_views.settings_view, name="settings"),
    path('settings/change_name', settings_views.change_name, name="change_name"),
    path('settings/change_email', settings_views.change_email, name="change_email"),
    path('settings/change_password', settings_views.change_password, name="change_password"),
    path('settings/delete_account', settings_views.delete_account, name="delete_account"),

]
