from rest_framework import generics
from django_filters import rest_framework as filters
from . import models


class ApartmentFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_apart_area = filters.NumberFilter(field_name='apartment_area', lookup_expr='gte')
    max_apart_area = filters.NumberFilter(field_name='apartment_area', lookup_expr='gte')

    class Meta:
        model = models.Apartment
        fields = ['adv_type', 'room_count', 'min_price', 'max_price', 'max_price', 'min_apart_area', 'max_apart_area',
                  'apartment_type', 'settlement_type', 'apartment_status', 'owner']


class ContactListFilter(filters.FilterSet):

    class Meta:
        model = models.Contact
        fields = ['user']
