from django.contrib import admin
from api.models import *

admin.site.register(House, admin.ModelAdmin)
admin.site.register(HouseImg, admin.ModelAdmin)
admin.site.register(HouseDoc, admin.ModelAdmin)
admin.site.register(HouseNew, admin.ModelAdmin)
admin.site.register(Block, admin.ModelAdmin)
admin.site.register(Section, admin.ModelAdmin)
admin.site.register(Standpipe, admin.ModelAdmin)
admin.site.register(Floor, admin.ModelAdmin)
admin.site.register(Apartment, admin.ModelAdmin)
admin.site.register(ApartImg, admin.ModelAdmin)
admin.site.register(Promotion, admin.ModelAdmin)
admin.site.register(User, admin.ModelAdmin)
