from django.test import TestCase
from ..serializers import ApartmentDetailSerializer
from ..models import Apartment


class ApartmentSerializerTestCase(TestCase):
    def test_ok(self):
        apartment_1 = Apartment.objects.create(document='Доверенность', room_count=1, apartment_type='Пентхаус',
                                               apartment_status='Требует ремонта', apartment_area=21.0,
                                               kitchen_area=11.0, loggia=1, heating_type='Газ', commission=112,
                                               description='test description', price=123213,
                                               address='Test address', apart_class='Студия, санузел', is_actual=0,
                                               created_date='2021-07-07 04:34:23.861943', owner_id=None)
        data = [ApartmentDetailSerializer(apartment_1).data]
        expected_data = [
            {'id': 3,
             'main_image': None,
             'price': 123213,
             'address': 'Test address',
             'adv_type': '',
             'apartment_status': 'Требует ремонта',
             'apartment_type': 'Пентхаус',
             'apart_class': 'Студия, санузел',
             'apartment_area': 21.0,
             'kitchen_area': 11.0,
             'loggia': True,
             'heating_type': 'Газ',
             'settlement_type': '',
             'commission': 112,
             'description': 'test description',
             'promotion': None,
             'owner': None}
        ]
        self.assertEqual(data, expected_data)
