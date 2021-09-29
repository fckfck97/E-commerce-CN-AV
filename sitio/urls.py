from django.urls import path

from .views import (
    remove_from_cart,
    add_to_cart,
    ProductView,
    HomeView,
    reduce_quantity_item,
    incre_quantity_item,
    OrderSummaryView,
    CheckoutView,
    SignUpView,
    Perfil
)

app_name = 'sitio'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary', OrderSummaryView.as_view(),name='order-summary'),
    path('reduce-quantity-item/<pk>/', reduce_quantity_item,name='reduce-quantity-item'),
    path('incre-quantity-item/<pk>/', incre_quantity_item,name='incre-quantity-item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('registrate/', SignUpView.as_view(), name='registrate'),
    path('perfil/<int:pk>/', Perfil.as_view(), name='perfil'),
]