from core.models import Product, Address, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, wishlist

def default(request):
    categories = Category.objects.all()
    address = Address.objects.all()
    
    return{
        'categories':categories,
        'address':address,
    }