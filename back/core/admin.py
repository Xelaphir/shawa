from django.contrib import admin
from .models import *


admin.site.register(Customer)

admin.site.register(ComponentType)
admin.site.register(Component)
admin.site.register(Discount)
admin.site.register(ComponentOwnership)
admin.site.register(DiscountOwnership)
admin.site.register(Lot)
admin.site.register(Recipe)
admin.site.register(RecipeComposition)
admin.site.register(Order)
admin.site.register(OrderComposition)
