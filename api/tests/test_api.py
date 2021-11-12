import json

from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .. import models
from ..models import Apartment

# Apartment create and list test
from ..serializers import ApartmentDetailSerializer


class ApartmentTestCase(APITestCase):
    def setUp(self):
        self.user = models.User.objects.create(email='test@gmail.com',
                                               password='123')
        self.client.force_login(self.user)
        self.apartment = Apartment.objects.create(document='Доверенность', room_count=1, apartment_type='Пентхаус',
                                                  apartment_status='Требует ремонта', apartment_area=21.0,
                                                  kitchen_area=11.0, loggia=1, heating_type='Газ', commission=112,
                                                  description='test description', price=123213,
                                                  address='Test address', apart_class='Студия, санузел', is_actual=0,
                                                  created_date='2021-07-07 04:34:23.861943', owner_id=None)

    def test_list(self):
        url = reverse('apartment-list')
        print(url)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_detail(self):
        url = '/api/apartment/1/'
        print(url)
        response = self.client.get(url)
        print(response.data)
        serialized_data = ApartmentDetailSerializer(self.apartment).data
        self.assertEqual(serialized_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
