from django.urls import path
from . import views


urlpatterns = [
    path('registration/', views.RegistrationAPIView.as_view(), name='user_registration'),
    path('login/', views.authenticate_user, name='user_login'),
    path('update/', views.UserRetrieveUpdateAPIView, name='user_update'),
    path('verificate/<phone>/', views.PhoneNumberRegistered.as_view(), name="phone-login"),
    path('apartment/', views.ApartmentList.as_view(), name='apartment-list'),
    path('apartment/<int:pk>/', views.ApartmentDetail.as_view(), name='apartment-detail'),
    path('apartment/create/', views.ApartmentCreate.as_view(), name='apartment-create'),
    path('floor/create/', views.FloorCreate.as_view(), name='floor-create'),
    path('contact/', views.ContactList.as_view(), name='contact-list'),
    path('contact/create', views.ContactCreate.as_view(), name='contact-create'),
    path('contact/<int:pk>', views.ContactUpdate.as_view(), name='contact-update'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('user/create', views.UserCreate.as_view(), name='user-create'),
    path('promotion/create', views.PromoCreate.as_view(), name='promotion-create'),
    path('house/', views.HouseList.as_view(), name='house-list'),
    path('house/<int:pk>', views.HouseDetail.as_view(), name='house-detail'),
    path('house/create', views.HouseCreate.as_view(), name='house-create'),
]
