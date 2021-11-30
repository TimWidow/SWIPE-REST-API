import json
from datetime import datetime

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
        self.apartment = Apartment.objects.create(document='OWNERSHIP', address='Test address', rooms=1,
                                                  apart_type='APARTMENT', apart_status='SHELL',
                                                  apart_layout='STUDIO',
                                                  apart_area=42.0, kitchen_area=21.0, loggia=True,
                                                  heating='GAS', payment='CAPITAL', contact='CALL',
                                                  price=10000, commission=1000,
                                                  description='test description', is_actual=True,
                                                  created=datetime.now())

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
