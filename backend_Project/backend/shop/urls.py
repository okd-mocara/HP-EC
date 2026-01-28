from django.urls import path
from .views import ProductListView, ProductDetailView, create_checkout_session, stripe_webhook

urlpatterns = [
    path("products", ProductListView.as_view()),
    path("products/<int:pk>", ProductDetailView.as_view()),
    path("checkout", create_checkout_session),
    path("stripe/webhook", stripe_webhook),
]
