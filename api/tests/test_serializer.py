from datetime import datetime

from django.test import TestCase
from ..serializers import ApartmentDetailSerializer
from ..models import Apartment


class ApartmentSerializerTestCase(TestCase):
    def test_ok(self):
        apartment_1 = Apartment.objects.create(document='OWNERSHIP', address='Test address',
                                               number=1, rooms=1,
                                               apart_type='APARTMENT', apart_status='SHELL',
                                               apart_layout='STUDIO',
                                               apart_area=42.0, kitchen_area=21.0, loggia=True,
                                               heating='GAS')
        data = [ApartmentDetailSerializer(apartment_1).data]
        print(data)
        exp_data = [
            {'house': None,
             'floor': None,
             'document': 'OWNERSHIP',
             'address': 'Test address',
             'rooms': 1,
             'apart_type': 'APARTMENT',
             'apart_status': 'SHELL',
             'apart_layout': 'STUDIO',
             'apart_area': 42.0,
             'kitchen_area': 21.0,
             'loggia': True,
             'heating': 'GAS',
             }
        ]
        print(exp_data)
        self.assertEqual(data, exp_data)
