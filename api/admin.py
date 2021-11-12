from django.contrib import admin
from api.models import Apartment, Floor, Section, House, User, PhoneModel


class ApartmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(Floor, ApartmentAdmin)
admin.site.register(Section, ApartmentAdmin)
admin.site.register(House, ApartmentAdmin)
admin.site.register(User, ApartmentAdmin)
admin.site.register(PhoneModel, ApartmentAdmin)
