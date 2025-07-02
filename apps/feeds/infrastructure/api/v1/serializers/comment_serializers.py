from rest_framework import serializers
from apps.feeds.domain.entities.comment import Comment
from apps.custom_auth.domain.entities.user import User


class CommentAuthorSerializer(serializers.ModelSerializer):
    """Minimal user serializer for comment authors"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']


class CommentSerializer(serializers.ModelSerializer):
    """Basic comment serializer"""
    author = CommentAuthorSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id',
            'content',
            'author',
            'parent_comment',
            'likes_count',
            'replies_count',
            'is_liked',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'author',
            'likes_count',
            'replies_count',
            'is_liked',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
    
    def get_replies_count(self, obj):
        """Get count of non-deleted replies"""
        return obj.replies.filter(is_deleted=False).count()
    
    def get_is_liked(self, obj):
        """Check if current user has liked the comment"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        from apps.feeds.domain.entities.like import Like
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(Comment)
        return Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=obj.id
        ).exists()


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    
    class Meta:
        model = Comment
        fields = [
            'content',
            'parent_comment'
        ]
    
    def validate_content(self, value):
        """Validate comment content"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Content cannot exceed 1000 characters")
        return value.strip()
    
    def validate_parent_comment(self, value):
        """Validate parent comment"""
        if value and value.is_deleted:
            raise serializers.ValidationError("Cannot reply to deleted comment")
        return value


class CommentDetailSerializer(CommentSerializer):
    """Detailed comment serializer with replies"""
    replies = serializers.SerializerMethodField()
    
    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ['replies']
    
    def get_replies(self, obj):
        """Get comment replies (limited depth)"""
        if obj.get_level() >= 3:  # Limit nesting depth
            return []
        
        replies = obj.replies.filter(is_deleted=False).order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data


class CommentThreadSerializer(serializers.ModelSerializer):
    """Serializer for comment threads with full hierarchy"""
    author = CommentAuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id',
            'content',
            'author',
            'likes_count',
            'replies',
            'user_has_liked',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'author',
            'likes_count',
            'user_has_liked',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
    
    def get_replies(self, obj):
        """Get all replies recursively"""
        if obj.thread_depth >= 5:  # Hard limit for recursion
            return []
        
        replies = obj.replies.filter(is_deleted=False).order_by('created_at')
        return CommentThreadSerializer(replies, many=True, context=self.context).data
    
    def get_user_has_liked(self, obj):
        """Check if current user has liked the comment"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        from apps.feeds.domain.entities.like import Like
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(Comment)
        return Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=obj.id
        ).exists()
