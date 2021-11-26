from django_filters import rest_framework as filters
from .models import Apartment, User


class ApartmentFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_apart_area = filters.NumberFilter(field_name='apart_area', lookup_expr='gte')
    max_apart_area = filters.NumberFilter(field_name='apart_area', lookup_expr='lte')

    class Meta:
        model = Apartment
        fields = ['rooms', 'min_price', 'max_price', 'min_apart_area', 'max_apart_area',
                  'apart_type', 'apart_status', 'apart_layout', 'payment', 'owner']


class ContactListFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = ['phone']
