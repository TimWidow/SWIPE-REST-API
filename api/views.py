import mimetypes

import jwt
from dj_rest_auth.app_settings import TokenSerializer
from dj_rest_auth.models import TokenModel
from dj_rest_auth.utils import jwt_encode
from django.contrib.auth import (
    login as django_login,
    logout as django_logout
)
from django.contrib.auth import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import escape_uri_path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.generics import *
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from swipe import settings
from . import filters as my_filter
from .filters import *
from .permissions import *
from .serializers import *
from .verify import send

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)


def create_token(token_model, user):
    token, _ = token_model.objects.get_or_create(user=user)
    return token


class RegistrationAPIView(GenericAPIView):
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
        user = serializer.save()
        print(user)
        user.key = serializer.data.get('token', None)
        user.save()

        return Response(
            {
                'token': user.key,
            },
            status=status.HTTP_201_CREATED,
        )


class APILoginView(GenericAPIView):
    """
        Check the credentials and return the REST Token
        if the credentials are valid and authenticated.
        Calls Django Auth login method to register User ID
        in Django session framework

        Accept the following POST parameters: email, password
        Return the REST Framework Token Object's key.
        """
    permission_classes = (AllowAny,)
    serializer_class = APILoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(APILoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    @staticmethod
    def get_response_serializer():
        if getattr(settings, 'REST_USE_JWT', False):
            response_serializer = JWTSerializer
        else:
            response_serializer = TokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']

        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        response = Response(serializer.data, status=status.HTTP_200_OK)

        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()


class PhoneAuthenticationView(GenericAPIView):
    """
        Check the phone number and send SMS with 4-digit code
    """
    permission_classes = (AllowAny,)
    serializer_class = PhoneAuthenticationSerializer

    def post(self, request, *args, **kwargs):
        serializer = PhoneAuthenticationSerializer(data=self.request.data)

        if serializer.is_valid():
            print(serializer.validated_data)
            user = serializer.validated_data['user']
            if user:
                send(user.phone)
                return Response({'sms': 'sent'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class TokenAuthenticationView(GenericAPIView):
    """
        Check registration token and log in
    """
    permission_classes = (AllowAny,)
    serializer_class = TokenAuthenticationSerializer

    def login(self, user):
        django_login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

    def post(self, request, *args, **kwargs):
        serializer = TokenAuthenticationSerializer(data=self.request.data)

        if serializer.is_valid():
            print(serializer.validated_data)
            try:
                user = serializer.validated_data['user']
                if user:
                    self.login(user)
                    user.key = None
                    user.save()
                    return Response({str(user.phone): 'logged in'}, status=status.HTTP_200_OK)

            except TypeError:
                return Response(serializer.validated_data, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)




class PhoneLoginView(GenericAPIView):
    """
        Check the credentials and return the REST Token
        if the credentials are valid and authenticated.
        Calls Django Auth login method to register User ID
        in Django session framework

        Accept the following POST parameters: email, password
        Return the REST Framework Token Object's key.
        """
    permission_classes = (AllowAny,)
    serializer_class = PhoneLoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PhoneLoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user, backend='django.contrib.auth.backends.ModelBackend')

    @staticmethod
    def get_response_serializer():
        if getattr(settings, 'REST_USE_JWT', False):
            response_serializer = JWTSerializer
        else:
            response_serializer = TokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']

        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        response = Response(serializer.data, status=status.HTTP_200_OK)

        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()


class APILogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    @staticmethod
    def logout(request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        if getattr(settings, 'REST_SESSION_LOGIN', True):
            django_logout(request)

        response = Response({"detail": "Successfully logged out."},
                            status=status.HTTP_200_OK)
        return response


class ApartmentList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApartmentListSerializer
    queryset = Apartment.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ApartFilter


class ApartmentDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    queryset = Apartment.objects.all()
    serializer_class = ApartmentDetailSerializer


class FloorList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApartmentListSerializer
    queryset = Floor.objects.all()


class ContactList(ListAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = ContactListSerializer
    queryset = User.objects.all()
    filterset_class = my_filter.ContactListFilter


class ContactCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactCreateSerializer

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class ContactUpdate(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = ContactSerializer


class UserDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class = UserSerializer
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    queryset = User.objects.all()


class UserCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


class PromoCreate(CreateAPIView):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class = PromotionSerializer


class HouseAllViewSet(ListModelMixin,
                      RetrieveModelMixin,
                      GenericViewSet):
    """
    Api is available for any users even if they are not authenticated
    """
    permission_classes = (AllowAny,)
    authentication_classes = []
    queryset = House.objects.all().order_by('-id')
    serializer_class = HouseSerializer
    view_tags = ['Houses']

    @action(detail=False)
    def list(self, request, *args, **kwargs):
        queryset = House.objects.all()
        serializer = HouseSerializer(queryset, many=True)
        return Response(serializer.data)


class HouseCreate(CreateAPIView):
    """
    "property_type" SECONDARY - Вторичный рынок, NEW - Новостройки, COTTAGE - Коттедж
    "house_leased" LEASED - Сдан, NOT LEASED - Не сдан
    "house_status" ECO - Эконом, COMFORT - Комфорт, COMFORT - Бизнес, ELITE - Элитный
    "house_type" MULTI - Многоквартирный, PRIVATE - Частный
    "technology" MONO - Монолитный, PANEL - Панельный, BRICK - Кирпич
    "territory" CLOSED - Закрытая, OPEN - Открытая
    "heating" CENTRAL - Центральное, PERSONAL - Индивидуальное
    "sewerage" CENTRAL - Центральная, PIT - Яма
    "water" CENTRAL - Центральное , AUTO - Автономное
    """
    permission_classes = [IsAuthenticated]
    serializer_class = HouseCreateSerializer


class ApartmentCreate(CreateAPIView):
    """
       "document" OWNERSHIP - Документ собственности, POA - Доверенность
       "apart_type" APARTMENT - Апартаменты, PENTHOUSE - Пентхаус
       "apart_status" SHELL - Черновая, EURO - Евроремонт, REPAIR - Требует ремонта, FULL REPAIR - Требуется капитальный ремонт
       "apart_layout" STUDIO - Студия, GUEST - Гостинка, SMALL - Малосемейка, ISOLATED - Изолированные комнаты, ADJOINING - Смежные комнаты, FREE - Свободная планировка
       "heating" GAS - Газовое, ELECTRO - Электрическое, WOOD - Дрова
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ApartmentCreateSerializer

    # def perform_create(self, serializer):
    #    serializer.validated_data['owner'] = self.request.user
    #    serializer.save()


class BlockCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BlockCreateSerializer


class SectionCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SectionCreateSerializer


class FloorCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FloorCreateSerializer


class SectionViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Section.objects.all().order_by('-id')
    serializer_class = SectionSerializer
    view_tags = ['Sections']

    def get_queryset(self):
        if self.request.query_params.get('building'):
            return self.queryset.filter(building__pk=self.request.query_params.get('building'))
        if self.request.query_params.get('house'):
            return self.queryset.filter(building__house__pk=self.request.query_params.get('house'))
        return self.queryset


class FloorViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Floor.objects.all().order_by('-id')
    serializer_class = FloorSerializer
    view_tags = ['Floors']

    def get_queryset(self):
        if self.request.query_params.get('section'):
            return self.queryset.filter(section__pk=self.request.query_params.get('section'))
        if self.request.query_params.get('house'):
            return self.queryset.filter(section__building__house__pk=self.request.query_params.get('house'))
        return self.queryset


class HouseNewsViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = HouseNew.objects.all().order_by('-id')
    serializer_class = HouseNewSerializer
    view_tags = ['HouseNew']

    def list(self, request, *args, **kwargs):
        """ Filter news by house """
        queryset = self.queryset.filter(house__pk=request.query_params.get('house'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DocumentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = HouseDoc.objects.all().order_by('-id')
    serializer_class = HouseDocSerializer
    view_tags = ['Documents']

    def list(self, request, *args, **kwargs):
        """ Filter documents by house """
        queryset = self.queryset.filter(house__pk=request.query_params.get('house'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def generate_http_response_to_download(instance):
        """
        Get instance of available models and generate HttpResponse with file - to download
        :param instance: Document, Attachment
        :return: HttpResponse
        """

        with open(instance.file.path, 'rb') as file:
            file_name = instance.file.name.split('/')[-1].encode('utf-8')

            response = HttpResponse(file, content_type=mimetypes.guess_type(instance.file.name)[0])
            response['Content-Disposition'] = f'attachment; filename={escape_uri_path(file_name)}'
            return response

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.generate_http_response_to_download(instance)


class ApartViewSet(GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Apartment.objects.all().order_by('-id')
    serializer_class = ApartSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ApartFilter
    view_tags = ['Apartments']


class HouseViewSet(ModelViewSet):
    """
       Api is available for authenticated users
       """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = House.objects.all().order_by('-id')
    serializer_class = HouseDetailSerializer
    view_tags = ['Houses']

    def get_queryset(self):
        return House.objects.filter(sales_department=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(sales_department=self.request.user)


class HousePublic(ListModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    """
    Api is available for any users even if they are not authenticated
    """
    permission_classes = (AllowAny,)
    authentication_classes = []
    queryset = House.objects.all().order_by('-id')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HouseFilter
    serializer_class = HouseSerializer
    view_tags = ['Public-Houses']


class ApartPublic(ListModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    """
    This api is available for any users. Even if they are not authenticated
    """
    permission_classes = (AllowAny,)
    authentication_classes = []
    queryset = Apartment.objects.all().order_by('-id')
    serializer_class = ApartSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ApartFilter
    view_tags = ['Public-Apartments']

    def get_queryset(self):
        if self.request.query_params.get('house__pk'):
            return self.queryset.filter(floor__section__block__house__pk=self.request.query_params.get('house__pk'))
        elif self.request.query_params.get('client_pk'):
            return self.queryset.filter(client__pk=self.request.query_params.get('client_pk'))
        else:
            return self.queryset


class Booking(APIView):
    permission_classes = (IsAuthenticated,)
    view_tags = ['Apartments']

    def patch(self, request, pk):
        """
        patch: If booking == '1' and not apart.client - set new one.
               If booking == '0' checks condition. Sets client as None can only either current client or house owner
               Otherwise it will return error message in response
        :param request: {'booking': '1'} or {'booking': '0'}
        :param pk: apart pk
        :param format:
        :return: Response
        """
        apart = get_object_or_404(Apartment, pk=pk)
        is_house_owner = (apart.floor.section.block.house.sales_department == request.user)
        if request.data.get('booking') == '1' and not apart.client:
            apart.client = request.user
            apart.booked = True

            data_for_request = {
                'house': apart.floor.section.block.house.pk,
                'apart': apart.pk
            }
            serializer = RequestToChessSerializer(data=data_for_request)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({'Error': _('Error while creating request to chest. Connect to administration')})
        elif request.data.get('booking') == '0':
            if apart.client == request.user or is_house_owner:
                apart.client = None
                apart.booked = False
                apart.owned = False
                request_to_chest = get_object_or_404(RequestToChess, apart=apart)
                request_to_chest.delete()
            else:
                return Response({'Error': _('You cannot remove current client from this apart')},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Error': _('You cant book this apart')}, status=status.HTTP_400_BAD_REQUEST)
        apart.save()
        return Response({'pk': apart.pk,
                         'user_pk': request.user.pk,
                         'status': apart.booking_status}, status=status.HTTP_200_OK, )


class RequestToChestApi(ListModelMixin,
                        RetrieveModelMixin,
                        UpdateModelMixin,
                        DestroyModelMixin,
                        GenericViewSet):
    """ Manage requests to chest. Only house`s sales department can get its requests """
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = RequestToChess.objects.all().order_by('-id')
    serializer_class = RequestToChessSerializer
    view_tags = ['aparts']

    def get_queryset(self):
        return self.queryset.filter(house__sales_department=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        apart = instance.apart
        apart.booked = False
        apart.owned = False
        apart.client = None
        apart.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
