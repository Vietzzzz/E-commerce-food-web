from django.contrib import admin
from userauths.models import User, ContactUs


class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "bio"]
    
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject']


admin.site.register(User, UserAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
