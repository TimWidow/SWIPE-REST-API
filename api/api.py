from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from phone_verify.api import VerificationViewSet
from phone_verify import serializers as phone_serializers

from . import services, serializers


class VerificationViewSet(VerificationViewSet):

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny], serializer_class=serializers.VerificationSerializer)
    def verify_and_register(self, request):
        """Function to verify phone number and register a user

        Most of the code here is corresponding to the "verify" view already present in the package.

        """

        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Add your custom code here.
        # An example is shown below:

        serializer = serializers.YourUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.create_user_account(**serializer.validated_data)

        return Response(serializer.data)