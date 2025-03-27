from core.models import Product, Address, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, wishlist

def default(request):
    categories = Category.objects.all()
    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None
    return{
        'categories':categories,
        'address':address,
    }