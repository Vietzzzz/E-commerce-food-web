from django.urls import path
from useradmin import views

app_name = "useradmin"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", views.products, name="products"),
    path("add-product/", views.add_product, name="add_product"),
    path("edit-product/<pid>/", views.edit_product, name="edit_product"),
    path("delete_product/<pid>/", views.delete_product, name="delete_product"),
    path("orders/", views.orders, name="orders"),
    path("order_detail/<id>/", views.order_detail, name="order_detail"),
]
