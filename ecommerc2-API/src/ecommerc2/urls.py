from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from carts.views import (
    CartView,
    CheckoutFinalView,
    CheckoutView,
    ItemCountView,
)
from newsletter.views import (
    contact,
    home,
)
from orders.views import (
    AddressSelectFormView,
    OrderDetailView,
    OrderListView,
    UserAddressCreateView,
    UserCheckoutAPI,
)
from products.views import (
    APIHomeView,
    CategoryListAPIView,
    CategoryRetriveAPIView,
    ProductListAPIView,
    ProductRetriveAPIView,
)
from .views import about

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^about/$', about, name='about'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^products/', include('products.urls')),
    url(r'^categories/', include('products.urls_categories')),

    url(r'^orders/$', OrderListView.as_view(), name='orders'),
    url(r'^orders/(?P<pk>\d+)/$', OrderDetailView.as_view(), name='order_detail'),

    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^cart/count/$', ItemCountView.as_view(), name='item_count'),

    url(r'^checkout/$', CheckoutView.as_view(), name='checkout'),
    url(r'^checkout/address/$', AddressSelectFormView.as_view(), name='order_address'),
    url(r'^checkout/address/add/$', UserAddressCreateView.as_view(), name='user_address_create'),
    url(r'^checkout/final/$', CheckoutFinalView.as_view(), name='checkout_final'),
]


# API Patterns
urlpatterns += [
    url(r'^api/$', APIHomeView.as_view(), name='home_api'),
    url(r'^api/user/checkout/$', UserCheckoutAPI.as_view(), name='user_api'),
    url(r'^api/categories/$', CategoryListAPIView.as_view(), name='category_list_api'),
    url(r'^api/categories/(?P<pk>\d+)/$', CategoryRetriveAPIView.as_view(), name='category_detail_api'),
    url(r'^api/products/$', ProductListAPIView.as_view(), name='product_list_api'),
    url(r'^api/products/(?P<pk>\d+)/$', ProductRetriveAPIView.as_view(), name='product_detail_api'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)