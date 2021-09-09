from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist                      
from django.shortcuts import render, get_object_or_404, redirect                      
from django.views.generic import ListView, DetailView, View, CreateView                   
from django.utils import timezone   
from .forms import CheckoutForm,SignUpForm                    
from .models import (                           
    Item,
    Order,
    OrderItem,
    Perfil
)

#vista del registro de usuarios
class SignUpView(CreateView):
    model = Perfil
    form_class = SignUpForm
    template_name = "perfil_form.html"
    def post(self, request, *args, **kwargs):
        form = SignUpForm()
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.refresh_from_db() 
                user.save()
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=user.username, password=raw_password)
                login(request, user)
                messages.info(request,'Se han Guardado los Datos Correctamente')
                return redirect('/')
            else:
                form = self.form_class
                messages.info(request,'Usuario ya registrado intenta con otro nickname')
                
        return render(request, self.template_name, {'form': form})

# Create your views here.
class HomeView(ListView):
    model = Item
    template_name = "home.html"
    def post(self, request, *args, **kwargs):
        if 'nombre_producto' in request.POST:
            item_nombre = request.POST['nombre_producto']
            producto = Item.objects.filter(item_nombre__contains=item_nombre)
            existencia = Item.objects.filter(item_nombre__contains=item_nombre).exists()
            if existencia == True:
                return render(request, self.template_name, {'object_list': producto})
            else:
                todo = Item.objects.all()
                messages.info(request,'El Producto que buscas no esta en el Inventario')
                return render(request, self.template_name, {'object_list': todo}) 

class ProductView(DetailView):
    model = Item
    template_name = "product.html"

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object' : order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "No tienes ningun articulo en tu carrito")
            return redirect("/")

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                direccion1 = form.cleaned_data.get('direccion1')
                direccion2 = form.cleaned_data.get('direccion2')
                ciudad = form.cleaned_data.get('ciudad')
                zip = form.cleaned_data.get('zip')
                
                checkout_address = CheckoutAddress(
                    user=self.request.user,
                    direccion1=direccion1,
                    direccion2=direccion2,
                    ciudad=ciudad,
                    zip=zip
                )
                checkout_address.save()
                order.checkout_address = checkout_address
                order.save()
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("sitio:order-summary")

@login_required
def add_to_cart(request, pk) :
    item = get_object_or_404(Item, pk = pk )
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user=request.user, ordered= False)

    if order_qs.exists() :
        order = order_qs[0]
        
        if order.items.filter(item__pk = item.pk).exists() :
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Articulo \""+order_item.item.item_nombre+"\" se ha Agregado al Carrito")
            return redirect("sitio:product", pk = pk)
        else:
            order.items.add(order_item)
            messages.info(request, "Articulo \""+order_item.item.item_nombre+"\" se ha Agregado al Carrito")
            return redirect("sitio:product", pk = pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, "Se ha Agregado al Carrito")
        return redirect("sitio:product", pk = pk)

@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.info(request, "Articulo \""+order_item.item.item_nombre+"\" se ha Removido del Carrito")
            return redirect("sitio:order-summary")
        else:
            messages.info(request, "Articulo \""+order_item.item.item_nombre+"\" se ha Removido del Carrito")
            return redirect("sitio:order-summary")
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("sitio:order-summary")


@login_required
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_qs = Order.objects.filter(
        user = request.user, 
        ordered = False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists() :
            order_item = OrderItem.objects.filter(
                item = item,
                user = request.user,
                ordered = False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "Has Reducido la compra del Articulo \""+order_item.item.item_nombre+"\" ")
            return redirect("sitio:order-summary")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("sitio:order-summary")
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("sitio:order-summary")

@login_required
def incre_quantity_item(request, pk):
    item = get_object_or_404(Item, pk = pk )
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user=request.user, ordered= False)

    if order_qs.exists() :
        order = order_qs[0]
        
        if order.items.filter(item__pk = item.pk).exists() :
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Se Ha incrementado la compra del Articulo  \""+order_item.item.item_nombre+"\"")
            return redirect("sitio:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Se ha Agregado al Carrito")
            return redirect("sitio:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, "Se ha Agregado al Carrito")
        return redirect("sitio:order-summary")