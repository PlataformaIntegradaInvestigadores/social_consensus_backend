from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from apps.custom_auth.models import Post
from apps.custom_auth.infrastructure.api.v1.serializers.post_serializer import PostSerializer


class PostCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """Asigna el usuario actual al crear una nueva publicación."""
        serializer.save(user=self.request.user)


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Obtiene las publicaciones de un usuario específico si se proporciona un `user_id`."""
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Post.objects.filter(user_id=user_id).order_by('-created_at')
        return Post.objects.none()


class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtra las publicaciones para asegurarse de que el usuario actual solo pueda eliminar sus propias publicaciones."""
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
