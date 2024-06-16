from django.forms import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers.user_serializer import UserListSerializer, UserSerializer, RegisterSerializer, UserTokenObtainPairSerializer
from apps.custom_auth.models import User


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        obj = super().get_object()
        if obj.id != self.request.user.id:
            raise PermissionDenied(
                "You do not have permission to edit this user.")
        return obj

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response(self.format_errors(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def format_errors(self, errors):
        custom_errors = {}
        for field, field_errors in errors.items():
            custom_errors[field] = [self.get_custom_error_message(
                field, error) for error in field_errors]
        return {'errors': custom_errors}

    def get_custom_error_message(self, field, error):
        custom_messages = {
            'username': {
                'user with this username already exists.': "User with this EMAIL already exists."
            },
            'scopus_id': {
                'user with this scopus id already exists.': "User with this SCOPUS ID already exists."
            }
        }
        return custom_messages.get(field, {}).get(error, error)
