from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.edit import UpdateView
from marketplace.models import Product
from django.core.paginator import Paginator
from marketplace.forms import ProductModelForm
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import stripe
from django.conf import settings
from accounts.models import UserLibrary

stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(View):

	def get(self, request, *args, **kwargs):
		products = Product.objects.filter(active=True)
		form = ProductModelForm()

		digital_products_data = None

		if products:
			paginator = Paginator(products, 9)
			page_number = request.GET.get('page')
			digital_products_data = paginator.get_page(page_number)

		context = {
			'products':digital_products_data,
			'form': form
		}
		return render(request, 'pages/index.html', context)

	def post(self, request, *args, **kwargs):
		products = Product.objects.filter(active=True)
		form = ProductModelForm()

		if request.method == 'POST':
			form = ProductModelForm(request.POST, request.FILES)
			if form.is_valid():
				form.user = request.user
				name = form.cleaned_data.get('name')
				description = form.cleaned_data.get('description')
				thumbnail = form.cleaned_data.get('thumbnail')
				slug = form.cleaned_data.get('slug')
				content_url = form.cleaned_data.get('content_url')
				content_file = form.cleaned_data.get('content_file')
				price = form.cleaned_data.get('price')
				active = form.cleaned_data.get('active')

				p, created = Product.objects.get_or_create(user=form.user,name=name,description=description, thumbnail=thumbnail, slug=slug, content_url=content_url, content_file=content_file, price=price, active=active)
				p.save()
				return redirect('home')

		digital_products_data = None

		if products:
			paginator = Paginator(products, 9)
			page_number = request.GET.get('page')
			digital_products_data = paginator.get_page(page_number)

		context = {
			'products':digital_products_data
		}
		return render(request, 'pages/index.html', context)

class UserProductListView(View):
	def get(self, request, *args, **kwargs):
		products = Product.objects.filter(user=self.request.user)
		context = {
			'products':products
		}
		return render(request, 'pages/products/user_productlist.html', context)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
	template_name = 'pages/products/edit.html'
	form_class = ProductModelForm

	def get_queryset(self):
		return Product.objects.filter(user=self.request.user)

	def get_success_url(self):
		return reverse("product-list")

class ProductDetailView(View):
	def get(self, request, slug, *args, **kwargs):
		product = get_object_or_404(Product, slug=slug)
		context = {
			'product':product,
		}
		context.update({
			'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
		})
		return render(request, 'pages/products/detail.html', context)

class CreateCheckoutSessionView(View):
	def post(self, request, *args, **kwargs):
		session = stripe.checkout.Session.create(
			payment_method_types=['card'],
			line_items=[{
			'price_data': {
				'currency': 'usd',
				'product_data': {
					'name': 'T-shirt',
					},
				'unit_amount': 2000,
			},
			'quantity': 1,
			}],
			mode='payment',
			success_url='https://example.com/success',
			cancel_url='https://example.com/cancel',
		  )

		return JsonResponse({
			id:session.id
		})

class UserLibraryView(LoginRequiredMixin, View):
	def get(self, request, username, *args, **kwargs):
		user = get_object_or_404(User, username=username)
		userlibrary = UserLibrary.objects.get(user=user)
		context = {
			'userlibrary':userlibrary
		}
		return render(request, 'pages/products/library.html', context)
