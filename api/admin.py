from django.contrib import admin
from api.models import Apartment, Floor, Section, House, User


admin.site.register(Apartment, admin.ModelAdmin)
admin.site.register(Floor, admin.ModelAdmin)
admin.site.register(Section, admin.ModelAdmin)
admin.site.register(House, admin.ModelAdmin)
admin.site.register(User, admin.ModelAdmin)
