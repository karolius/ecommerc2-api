from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic import FormView

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import AddressForm, UserAddressForm
from .mixins import CartOrderMixin, LoginRequiredMixin
from .models import (
    Order,
    UserAddress,
    UserCheckout,
)


User = get_user_model()


class UserCheckoutMixin(object):
    def user_failure(self, message=None):
        data = {
            "message": "There was an error. Please try again later",
            "success": False
        }
        if message:
            data["message"] = message
        return data

    def get_checkout_data(self, user=None, email=None):
        user_checkout = None
        data = {}
        if user and not email:
            if user.is_authenticated():
                if user.email:
                    user_checkout = UserCheckout.objects.get_or_create(user=user, email=user.email)[0]
                else:
                    user_checkout = UserCheckout.objects.get_or_create(user=user)[0]
        elif email:
            if not user:
                user_exists = User.objects.filter(email=email).count()
                if user_exists != 0:
                    return self.user_failure(message="This user already exists, please login.")
            try:
                user_checkout = UserCheckout.objects.get_or_create(email=email)[0]
                if user:
                    user_checkout.user = user
                    user_checkout.save()
            except:
                pass

        if user_checkout:
            data["token"] = user_checkout.get_client_token()
            data["braintree_id"] = user_checkout.get_braintree_id()
            data["user_checkout_id"] = user_checkout.id
            data["succes"] = True
        return data


class UserCheckoutAPI(UserCheckoutMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        data = self.get_checkout_data(user=request.user)
        return Response(data)

    def post(self, request, format=None):
        email = request.data.get("email")
        user = request.user
        if user.is_authenticated():
            if email == user.email:
                data = self.get_checkout_data(user=user, email=email)
            else:
                data = self.get_checkout_data(user=user)
        elif email and not user.is_authenticated():
            data = self.get_checkout_data(email=email)
        else:
            data = self.user_failure(message="Make sure you are authenticated or using a valid email.")
        return Response(data)


class OrderDetailView(DetailView):
    model = Order

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated(): # in case: in session is someone else, not loggeed user
            user_checkout = UserCheckout.objects.get(user=user)
        else:
            try:
                user_checkout_id = request.session.get("user_checkout_id")
                user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            except:
                user_checkout = None

        obj = self.get_object()
        if user_checkout and obj.user == user_checkout:
            return super(OrderDetailView, self).dispatch(request, *args, **kwargs)
        raise Http404


class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()

    def get_queryset(self):
        user_checkout_id = self.request.user.id
        user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        return super(OrderListView, self).get_queryset().filter(user=user_checkout)


class UserAddressCreateView(CreateView):
    form_class = UserAddressForm
    template_name = "forms.html"
    success_url = "/checkout/address/"

    def get_checkout_user(self):
        user_checkout_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        return user_checkout

    def form_valid(self, form, *args, **kwargs):
        form.instance.user = self.get_checkout_user()
        return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)


class AddressSelectFormView(CartOrderMixin, FormView):
    form_class = AddressForm
    template_name = "orders/address_select.html"

    def dispatch(self, *args, **kwargs):
        b_addr, s_addr = self.get_addresses()
        if b_addr.count() == 0:
            messages.success(self.request, "Please add a billing address before continuing")
            return redirect("user_address_create")
        elif s_addr.count() == 0:
            messages.success(self.request, "Please add a shipping address before continuing")
            return redirect("user_address_create")
        else:
            return super(AddressSelectFormView, self).dispatch(*args, **kwargs)

    def get_addresses(self, *args, **kwargs):
        user_checkout_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        b_addr = UserAddress.objects.filter(
            user=user_checkout,
            type="billing")
        s_addr = UserAddress.objects.filter(
            user=user_checkout,
            type="shipping")
        return b_addr, s_addr

    def get_form(self, *args, **kwargs):
        form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
        b_addr, s_addr = self.get_addresses()
        form.fields["billing_address"].queryset = b_addr
        form.fields["shipping_address"].queryset = s_addr
        return form

    def form_valid(self, form, *args, **kwargs):
        order = self.get_order()
        billing_address = form.cleaned_data["billing_address"]
        shipping_address = form.cleaned_data["shipping_address"]
        order.billing_address = billing_address
        order.shipping_address = shipping_address
        order.save()
        return super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return "/checkout/"