from django.urls import path
from products.views import product_view, review_view

urlpatterns = [
    path('products/', product_view, name="products"),
    path('reviews/', review_view, name="reviews")
]