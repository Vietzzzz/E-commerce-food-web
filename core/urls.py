from django.urls import path, include
from . import views


from core.views import (
    ajax_add_review,
    ajax_contact_form,
    category_list_view,
    category_product_list_view,
    delete_item_from_cart,
    index,
    make_address_default,
    product_detail_view,
    product_list_view,
    vendor_list_view,
    vendor_detail_view,
    tag_list,
    search_view,
    filter_product,
    add_to_cart,
    cart_view,
    update_cart,
    checkout,
    payment_completed_view,
    payment_failed_view,
    customer_dashboard,
    order_detail,
    wishlist_view,
    add_to_wishlist,
    remove_wishlist,
    contact,
    about_us,
    purchase_guide,
    privacy_policy,
    terms_of_service,
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
    # Search
    path("search/", search_view, name="search"),
    # Filter product URL
    path("filter-products/", filter_product, name="filter-product"),
    # Add to cart URL
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    # Cart Page URL
    path("cart/", cart_view, name="cart"),
    # Delete item from cart URL
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),
    # Update cart
    path("update-cart/", update_cart, name="update-cart"),
    # Checkout Page Url
    path("checkout/<oid>/", checkout, name="checkout"),
    # Paypal URL
    path("paypal/", include("paypal.standard.ipn.urls")),
    # Payment Successful
    path("payment-completed/<oid>/", payment_completed_view, name="payment-completed"),
    # Payment Failed
    path("payment-failed/", payment_failed_view, name="payment-failed"),
    # Dashboard URL
    path("dashboard/", customer_dashboard, name="dashboard"),
    # Order Detail URL
    path("dashboard/order/<int:id>", order_detail, name="order-detail"),
    # Make Default Address
    path("make-default-address/", make_address_default, name="make-default-address"),
    # Wishlist URL
    path("wishlist/", wishlist_view, name="wishlist"),
    # Add to wishlist
    path("add-to-wishlist/", add_to_wishlist, name="add-to-wishlist"),
    # Removing from wishlist
    path("remove-from-wishlist/", remove_wishlist, name="remove-from-wishlist"),
    path("contact/", contact, name="contact"),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),
    path("about_us/", about_us, name="about_us"),
    path("purchase_guide/", purchase_guide, name="purchase_guide"),
    path("privacy_policy/", privacy_policy, name="privacy_policy"),
    path("terms_of_service/", terms_of_service, name="terms_of_service"),
    # New routes
    path("save_checkout_info/", views.save_checkout_info, name="save_checkout_info"),
]
