from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
#creacion de los usuarios 

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, blank=True)
    web = models.URLField(blank=True)

    # Python 3
    def __str__(self): 
        return self.usuario.username

@receiver(post_save, sender=User)
def crear_usuario_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_usuario_perfil(sender, instance, **kwargs):
    instance.perfil.save()

CATEGORY = (
    ('J', 'Jarabes'),
    ('C', 'Capsulas'),
    ('P', 'Polvos')
)

LABEL = (
    ('N', 'Nuevo'),
    ('MV', 'Mejores Ventas')
)

ORGANO = (

    ('R', 'Riñones'),
    ('C', 'Corazonn'),
    ('P', 'Pulmones'),
    ('O', 'Ojos'),
    ('S', 'Sangre'),
    ('H', 'Higado'),
    ('C', 'Colon'),


)

class Item(models.Model):
    item_nombre = models.CharField(max_length=100)
    precio = models.FloatField()
    precio_descuento = models.FloatField(blank=True, null=True)
    categoria = models.CharField(choices=CATEGORY, max_length=2)
    etiqueta = models.CharField(choices=LABEL, max_length=2)
    organo = models.CharField(choices=ORGANO, max_length=2)

    descripcion = models.TextField()

    def __str__(self):
        return self.item_nombre

    def get_absolute_url(self):
        return reverse("sitio:product", kwargs={
            "pk" : self.pk
        
        })

    def get_add_to_cart_url(self):
        return reverse("sitio:add-to-cart", kwargs={
            "pk" : self.pk
        })

    def get_remove_from_cart_url(self):
        return reverse("sitio:remove-from-cart", kwargs={
            "pk" : self.pk
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.item_nombre}"

    def get_total_item_price(self):
        return self.quantity * self.item.precio

    def get_discount_item_price(self):
        return self.quantity * self.item.precio_descuento

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_discount_item_price()

    def get_final_price(self):
        if self.item.precio_descuento:
            return self.get_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model) :
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

class CheckoutAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=100)
    direccion2 = models.CharField(max_length=100)
    ciudad = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username