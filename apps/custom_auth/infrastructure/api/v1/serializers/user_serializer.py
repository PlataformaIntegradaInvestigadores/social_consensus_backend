from rest_framework import serializers


class RetiredIdentitySerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)
    canonical_service = serializers.CharField(read_only=True)


UserListSerializer = RetiredIdentitySerializer
UserSerializer = RetiredIdentitySerializer
RegisterSerializer = RetiredIdentitySerializer
UserTokenObtainPairSerializer = RetiredIdentitySerializer
