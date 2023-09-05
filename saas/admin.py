from django.contrib import admin
from .models import Task, Product, AliexpressProduct

# Register your models here.
admin.site.register(Task)
admin.site.register(Product)
admin.site.register(AliexpressProduct)