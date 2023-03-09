from django.contrib import admin

# Register your models here.

from .models import  User,Account,Transaction

admin.site.register(User)
admin.site.register(Account)
admin.site.register(Transaction)