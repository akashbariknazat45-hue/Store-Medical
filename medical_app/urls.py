from django.urls import path
from .views import *
urlpatterns = [
    #Athu Router
    path('login', user_login, name="login"),
    path('register', user_register, name="register"),
    path('logout', user_logout, name="logout"),
    path("change-password/", change_password, name="change_password"),
    
    # MANAGE ADDRESS
    path('manage-address/', manage_address, name='manage_address'),
    path('add-address/', add_address, name='add_address'),
    path('edit-address/<int:address_id>/', edit_address, name='edit_address'),
    path('delete-address/<int:address_id>/', delete_address, name='delete_address'),
    path('default-address/<int:address_id>/', default_address, name='default_address'),
    
    #Other router
    path('', home_func, name="home"),
    path('contact', contact_func, name="contact"),
    path("about/", about_func, name="about"),
    path('product/<slug:pslug>', get_product_detail_view, name = "get_product_detail_view"),
    path("add-to-favourites/<int:userid>/<int:pid>/",add_to_favourites,name="add_to_favourites"),
    path("favourites", favourites, name="favourites"),
    path("revome-from-favourites/<int:userid>/<int:pid>/",remove_from_favourites,name="remove_from_favourites"),
    path('cart', get_cart_items,name="cart"),
    path('remove-cart-item/<int:pid>/', delete_item_from_cart , name="remove_from_cart"),
    path('update-cart-item/', update_cart_item , name="update_cart_item"),
    path('add-to-cart', add_items_to_cart, name="add_items_to_cart"),
    path('checkout', checkout, name="checkout"), 
    path('process-order', process_order, name="process_order"),
    path('orders', user_orders, name="orders"),
    path("order/<str:orderid>", order_bill, name="order_bill"),
    path('cancel-order/<str:orderid>/', cancel_order, name="cancel_order"),
    path('payment-callback', payment_callback, name ="payment_callback"),
    # AI Routes
    path("ai-chat/", ai_chat, name="ai_chat"),
    

]
