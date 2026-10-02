from django.contrib.auth.models import User
from ..models import Medical_Favourite, Medical_Cart
from django import template
register = template.Library()

@register.simple_tag
def get_favourites_count(userid):
    user = User.objects.filter(id=userid).first()
    favourites_count = Medical_Favourite.objects.filter(user=user).count()
    return favourites_count


@register.simple_tag
def get_cart_count(userid):
    user = User.objects.filter(id=userid).first()
    carts_count = Medical_Cart.objects.filter(user=user).count()
    return carts_count

@register.simple_tag
def multiply(num1, num2):
    return num1*num2