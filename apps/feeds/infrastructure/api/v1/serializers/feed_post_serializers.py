from rest_framework import serializers
from apps.feeds.domain.entities.feed_post import FeedPost
from apps.feeds.domain.entities.post_file import PostFile
from apps.custom_auth.domain.entities.user import User


class PostFileSerializer(serializers.ModelSerializer):
    """Serializer for post file attachments"""
    
    class Meta:
        model = PostFile
        fields = [
            'id',
            'file',
            'file_type',
            'file_size',
            'filename',
            'created_at'
        ]
        read_only_fields = ['id', 'file_size', 'filename', 'created_at']


class AuthorSerializer(serializers.ModelSerializer):
    """Minimal user serializer for post authors"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']


class FeedPostSerializer(serializers.ModelSerializer):
    """Basic feed post serializer"""
    author = AuthorSerializer(read_only=True)
    files = PostFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = FeedPost
        fields = [
            'id',
            'content',
            'author',
            'files',
            'tags',
            'likes_count',
            'comments_count',
            'views_count',
            'shares_count',
            'engagement_score',
            'is_public',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'author',
            'likes_count',
            'comments_count', 
            'views_count',
            'shares_count',
            'engagement_score',
            'created_at',
            'updated_at'
        ]


class FeedPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating feed posts"""
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    
    class Meta:
        model = FeedPost
        fields = [
            'content',
            'tags',
            'is_public',
            'files'
        ]
    
    def validate_content(self, value):
        """Validate post content"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        if len(value) > 5000:
            raise serializers.ValidationError("Content cannot exceed 5000 characters")
        return value.strip()
    
    def validate_files(self, value):
        """Validate uploaded files"""
        if not value:
            return value
            
        if len(value) > 10:
            raise serializers.ValidationError("Cannot upload more than 10 files per post")
        
        total_size = sum(f.size for f in value)
        if total_size > 50 * 1024 * 1024:  # 50MB total limit
            raise serializers.ValidationError("Total file size cannot exceed 50MB")
        
        for file in value:
            if file.size > 10 * 1024 * 1024:  # 10MB per file
                raise serializers.ValidationError("Individual file size cannot exceed 10MB")
        
        return value
    
    def create(self, validated_data):
        """Create post with files"""
        files_data = validated_data.pop('files', [])
        post = FeedPost.objects.create(**validated_data)
        
        # Create file attachments
        for file_data in files_data:
            PostFile.objects.create(post=post, file=file_data)
        
        return post


class FeedPostDetailSerializer(FeedPostSerializer):
    """Detailed feed post serializer with comments preview"""
    recent_comments = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta(FeedPostSerializer.Meta):
        fields = FeedPostSerializer.Meta.fields + [
            'recent_comments',
            'user_has_liked'
        ]
    
    def get_recent_comments(self, obj):
        """Get recent comments preview"""
        from .comment_serializers import CommentSerializer
        recent_comments = obj.comments.filter(
            parent=None,
            is_deleted=False
        ).order_by('-created_at')[:3]
        return CommentSerializer(recent_comments, many=True, context=self.context).data
    
    def get_user_has_liked(self, obj):
        """Check if current user has liked the post"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        from apps.feeds.domain.entities.like import Like
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(FeedPost)
        return Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=obj.id
        ).exists()
