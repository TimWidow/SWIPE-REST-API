import jwt
from django.contrib.auth import user_logged_in
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework_jwt.serializers import jwt_payload_handler
from swipe import settings
from . import filters as my_filter
from rest_framework import generics
from django_filters import rest_framework as filters
from .filters import HouseFilter
from .models import House
from .permissions import IsOwnerOrSuperuserOrReadOnly, IsOwnerOrReadOnly
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .verify import send


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
def authenticate_by_email(request):
    print(request.data)
    try:
        email = request.data['email']
        password = request.data['password']
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


@api_view(['POST'])
@permission_classes([AllowAny, ])
def send_sms(request):
    print(request.data)
    phone = request.data['phone']
    send(phone)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_by_phone(request):
    print(request.data)
    try:
        phone = request.data['phone']
        user = auth.PhoneAuthBackend.authenticate(phone=phone)

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
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, IsAuthenticated]
    serializer_class = UserSerializer
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    queryset = User.objects.all()


class UserCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


class PromoCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PromotionSerializer


class HouseViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrSuperuserOrReadOnly)
    queryset = House.objects.all().order_by('-id')
    serializer_class = HouseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HouseFilter
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
    serializer_class = HouseSerializer
    view_tags = ['Public-Houses']


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
    queryset = Document.objects.all().order_by('-id')
    serializer_class = house_serializers.DocumentSerializer
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return generate_http_response_to_download(instance)


class FlatViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Flat.objects.all().order_by('-id')
    serializer_class = house_serializers.FlatSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FlatFilter
    view_tags = ['Flats']


class FlatPublic(ListModelMixin,
                 RetrieveModelMixin,
                 GenericViewSet):
    """
    This api is available for anu users. Even if the are not authenticated
    """
    permission_classes = (AllowAny,)
    authentication_classes = []
    queryset = Flat.objects.all().order_by('-id')
    serializer_class = house_serializers.FlatSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FlatFilter
    view_tags = ['Public-Flats']

    def get_queryset(self):
        if self.request.query_params.get('house__pk'):
            return self.queryset.filter(floor__section__building__house__pk=self.request.query_params.get('house__pk'))
        elif self.request.query_params.get('client_pk'):
            return self.queryset.filter(client__pk=self.request.query_params.get('client_pk'))
        else:
            return self.queryset


class BookingFlat(APIView):
    permission_classes = (IsAuthenticated,)
    view_tags = ['Flats']

    def patch(self, request, pk, format=None):
        """
        patch: If booking == '1' and not flat.client - set new one.
               If booking == '0' checks condition. Sets client as None can only either current client or house owner
               Otherwise it will return error message in response
        :param request: {'booking': '1'} or {'booking': '0'}
        :param pk: flat pk
        :param format:
        :return: Response
        """
        flat = get_object_or_404(Flat, pk=pk)
        is_house_owner = (flat.floor.section.building.house.sales_department == request.user)
        if request.data.get('booking') == '1' and not flat.client:
            flat.client = request.user
            flat.booked = True

            # After we booked flat - we have to send request to the house owner fro adding new info to house chest
            data_for_request = {
                'house': flat.floor.section.building.house.pk,
                'flat': flat.pk
            }
            serializer = house_serializers.RequestToChestSerializer(data=data_for_request)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({'Error': _('Error while creating request to chest. Connect to administration')})
        elif request.data.get('booking') == '0':
            if flat.client == request.user or is_house_owner:
                flat.client = None
                flat.booked = False
                flat.owned = False
                request_to_chest = get_object_or_404(RequestToChest, flat=flat)
                request_to_chest.delete()
            else:
                return Response({'Error': _('You cannot remove current client from this flat')},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Error': _('You cant book this flat')}, status=status.HTTP_400_BAD_REQUEST)
        flat.save()
        return Response({'pk': flat.pk,
                         'user_pk': request.user.pk,
                         'status': flat.booking_status}, status=status.HTTP_200_OK, )


class RequestToChestApi(ListModelMixin,
                        RetrieveModelMixin,
                        UpdateModelMixin,
                        DestroyModelMixin,
                        GenericViewSet):
    """ Manage requests to chest. Only house`s sales department can get its requests """
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = RequestToChest.objects.all().order_by('-id')
    serializer_class = house_serializers.RequestToChestSerializer
    view_tags = ['Flats']

    def get_queryset(self):
        return self.queryset.filter(house__sales_department=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        flat = instance.flat
        flat.booked = False
        flat.owned = False
        flat.client = None
        flat.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteStandpipe(DestroyModelMixin,
                      GenericViewSet):
    """ Only for deleting standpipes.
        For 'edit' action - user section view set and nested serializer
     """
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Standpipe.objects.all().order_by('-id')
    serializer_class = house_serializers.StandpipeSerializer
    view_tags = ['Sections']
