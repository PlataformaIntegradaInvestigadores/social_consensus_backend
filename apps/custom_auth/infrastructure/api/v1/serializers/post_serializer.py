from rest_framework import serializers
from apps.custom_auth.models import Post, PostFile


class PostFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostFile
        fields = ['file']


class PostSerializer(serializers.ModelSerializer):
    files = PostFileSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'description', 'files', 'created_at']  # Include 'id'

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        if 'user' in validated_data:
            validated_data.pop('user')

        files = request.FILES.getlist('files', [])
        post = Post.objects.create(user=user, **validated_data)
        for file in files:
            PostFile.objects.create(post=post, file=file)
        return post
