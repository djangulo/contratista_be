from rest_framework import viewsets, mixins, status, parsers, renderers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView


from accounts.models import User
from accounts.serializers import UserSerializer
from accounts.permissions import AllowPostFromUnregisteredUser, IsOwnerOrReadOnly


class RegisterUserViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    ViewSet for registering new users. It has a single POST method,
    with special permissions to allow unregistered users to send a POST
    request.
    """
    permission_classes = (AllowPostFromUnregisteredUser,)
    serializer_class = UserSerializer
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            User.objects.create_user(
                email=request.data['email'],
                username=request.data['username'],
                password=request.data['password']
            )
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    User viewset with all standard operations except POST.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )


class ThrottledObtainToken(APIView):
    """
    Throttled version of rest_framework.authtoken.ObtainAuthToken
    class.
    """
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'authtoken'
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'username': user.username, 'token': token.key})


throttled_obtain_token = ThrottledObtainToken.as_view()