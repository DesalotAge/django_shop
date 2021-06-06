from django.db import transaction
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import  Notebook, Smartphone, Category, LatestProducts, Cart, Customer, CartProduct
from .mixins import CategoryDetailMixin, CartMixin
from .forms import OrderForm
from .utils import recalc_cart


class BaseView(CartMixin, CategoryDetailMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_main_page('notebook', 'smartphone')
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart,
        }
        return render(request, 'base.html', context)


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):

    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs.get('ct_model')]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        return context

class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'


class AddToCartView(CartMixin, CategoryDetailMixin, View):
    
    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        ct_model = kwargs.get('ct_model')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id,
            final_price=product.price, 
        )
        if created:
            self.cart.products.add(cart_product)
            recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно добавлен')
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, CategoryDetailMixin, View):

    def get(self, request, *args, **kwargs):

        product_slug = kwargs.get('slug')
        ct_model = kwargs.get('ct_model')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id,
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)

        messages.add_message(request, messages.INFO, 'Товар успешно удален')
        return HttpResponseRedirect('/cart/')


class ChangeQtyView(CartMixin, CategoryDetailMixin, View):

    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        ct_model = kwargs.get('ct_model')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id, 
        )
        print(request.POST['qty'])
        cart_product.qty = int(request.POST['qty'][0])
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Количество изменено')
        return redirect(reverse('cart'))


class CartView(CartMixin, CategoryDetailMixin, View):
    
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()

        context = {
            'categories': categories,
            'cart': self.cart,
        }
        return render(request, 'cart.html', context)


class CheckoutView(CartMixin, View):
    
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        form = OrderForm(request.POST or None)
        context = {
            'categories': categories,
            'cart': self.cart,
            'form': form,
        }
        return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        if form.is_valid():
            customer = Customer.objects.get(user=request.user)
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            self.cart.in_order = True
            new_order.cart = self.cart
            new_order.save()
            self.cart.save()
            customer.related_orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Заказ оформлен')
            return redirect(reverse('base'))
        return redirect(reverse('checkout'))