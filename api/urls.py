from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.views.generic import TemplateView

from . import views
from rest_framework import routers

router = routers.SimpleRouter()


urlpatterns = [
    path('google_login/', TemplateView.as_view(template_name="index.html")),
    path('google_accounts/', include('allauth.urls')),
    path('logout/', LogoutView.as_view()),
    path('registration/', views.RegistrationAPIView.as_view(), name='registration'),
    path('login/', views.PhoneAuthenticationView.as_view(), name='phone_login'),
    path('verify/', views.PhoneLoginView.as_view(), name='sms_verification'),
    path('house/create', views.HouseViewSet.as_view(({'get': 'create'})), name='house-viewset'),
    path('houses/', views.HousePublic.as_view(({'get': 'list'})), name='houses-list'),
    path('apartments/', views.ApartPublic.as_view({'get': 'list'}), name='apartment-list'),
    path('apartment/<int:pk>/', views.ApartmentDetail.as_view(), name='apartment-detail'),
    path('apartment/create/', views.ApartmentCreate.as_view(), name='apartment-create'),
    path('floor/create/', views.FloorCreate.as_view(), name='floor-create'),
    path('contact/', views.ContactList.as_view(), name='contact-list'),
    path('contact/create', views.ContactCreate.as_view(), name='contact-create'),
    path('contact/<int:pk>', views.ContactUpdate.as_view(), name='contact-update'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('user/create', views.UserCreate.as_view(), name='user-create'),
    path('promotion/create', views.PromoCreate.as_view(), name='promotion-create'),

] + router.urls
