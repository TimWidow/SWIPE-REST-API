import jwt
from authy.api import AuthyApiClient
from django.contrib.auth import user_logged_in
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.serializers import jwt_payload_handler

from swipe import settings
from . import models, auth
from . import serializers
from . import filters as my_filter
from rest_framework import generics
from django_filters import rest_framework as filters

from .models import Apartment, Floor, House, User
from .permissions import IsOwnerOrSuperuserOrReadOnly
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import pyotp
import base64
from twilio.rest import Client
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, HouseDetailSerializer, HouseListSerializer, PromotionSerializer, \
    UserSerializer, ContactSerializer, ContactCreateSerializer, ContactListSerializer, ApartmentListSerializer, \
    FloorCreateSerializer, ApartmentCreateSerializer, ApartmentDetailSerializer


class RegistrationAPIView(APIView):
    """
    Registers a new user.
    """
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        """
        Creates a new User object.
        Username, email, and password are required.
        Returns a JSON web token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    try:
        email = request.data['email']
        password = request.data['password']
        print(email, password)

        user = auth.EmailAuthBackend.authenticate(email=email, password=password)
        if user:
            try:
                payload = jwt_payload_handler(user)
                print(payload)
                token = jwt.encode(payload, settings.SECRET_KEY)
                user_details = {'name': (
                    user.first_name), 'token': token}
                user_logged_in.send(sender=user.__class__,
                                    request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as error:
                print(error)
                raise error
        else:
            res = {
                'error': 'can not authenticate with the given credentials or the account has been deactivated'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'please provide a email and a password'}
        return Response(res)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    # Allow only authenticated users to access this url
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get(self, request, *args, **kwargs):
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        serializer = serializers.UserSerializer(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateKey:
    @staticmethod
    def return_value(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"


class PhoneNumberRegistered(APIView):
    @staticmethod
    def get(phone):
        authy_api = AuthyApiClient(settings.AUTHY_API_KEY)


class ApartmentList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApartmentListSerializer
    queryset = Apartment.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = my_filter.ApartmentFilter


class ApartmentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, IsAuthenticated]
    queryset = Apartment.objects.all()
    serializer_class = ApartmentDetailSerializer


class ApartmentCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApartmentCreateSerializer

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class FloorCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FloorCreateSerializer


class FloorList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApartmentListSerializer
    queryset = Floor.objects.all()


class ContactList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = ContactListSerializer
    queryset = User.objects.all()
    filterset_class = my_filter.ContactListFilter


class ContactCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactCreateSerializer

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class ContactUpdate(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = ContactSerializer


class UserDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    queryset = models.User.objects.all()


class UserCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


class PromoCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PromotionSerializer


class HouseList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HouseListSerializer
    queryset = House.objects.all()


class HouseCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HouseDetailSerializer


class HouseDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, IsAuthenticated]
    serializer_class = HouseDetailSerializer
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    queryset = House.objects.all()
