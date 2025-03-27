from django.urls import path
from . import views

from core.views import (
    ajax_add_review,
    category_list_view,
    category_product_list_view,
    index,
    product_detail_view,
    product_list_view,
    vendor_list_view,
    vendor_detail_view,
    tag_list,
)

app_name = "core"

urlpatterns = [
    # Homepage
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("product/<pid>/", product_detail_view, name="product-detail"),
    # Category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>", category_product_list_view, name="category-product-list"),
    # Vendor
    path("vendors/", vendor_list_view, name="vendor-list"),
    path("vendor/<vid>/", vendor_detail_view, name="vendor-detail"),
    # tags
    path("products/tag/<slug:tag_slug>/", tag_list, name="tags"),
    # Add review
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax_add_review"),
]
