from rest_framework import serializers
from apps.feeds.domain.entities.feed_post import FeedPost
from apps.feeds.domain.entities.post_file import PostFile
from apps.feeds.domain.entities.poll import Poll
from apps.custom_auth.domain.entities.user import User
from .poll_serializers import PollSerializer


class PostFileSerializer(serializers.ModelSerializer):
    """Serializer for post file attachments"""
    
    class Meta:
        model = PostFile
        fields = [
            'id',
            'file',
            'file_type',
            'file_size',
            'original_filename',
            'alt_text',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'file_size', 'original_filename', 'uploaded_at']


class AuthorSerializer(serializers.ModelSerializer):
    """Minimal user serializer for post authors"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']


class FeedPostSerializer(serializers.ModelSerializer):
    """Basic feed post serializer"""
    author = AuthorSerializer(read_only=True)
    files = PostFileSerializer(source='post_files', many=True, read_only=True)
    poll = PollSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = FeedPost
        fields = [
            'id',
            'content',
            'author',
            'files',
            'poll',
            'tags',
            'likes_count',
            'comments_count',
            'views_count',
            'shares_count',
            'engagement_score',
            'is_public',
            'is_liked',
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
            'is_liked',
            'created_at',
            'updated_at'
        ]
    
    def get_is_liked(self, obj):
        """Check if current user has liked this post"""
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            from apps.feeds.domain.entities.like import Like
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(obj)
            return Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False


class FeedPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating feed posts"""
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    poll_data = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
        help_text="Poll data as JSON string with 'question' and 'options' fields"
    )
    
    class Meta:
        model = FeedPost
        fields = [
            'content',
            'tags',
            'is_public',
            'files',
            'poll_data'
        ]
    
    def validate_poll_data(self, value):
        """Validate poll data"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Validating poll_data: {value} (type: {type(value)})")
        
        # Handle empty values
        if not value or value == '{}' or (isinstance(value, dict) and not value):
            logger.info("poll_data is empty, returning None")
            return None
        
        # Parse JSON string
        if isinstance(value, str):
            import json
            logger.info(f"poll_data is string, parsing: {value}")
            try:
                value = json.loads(value)
                logger.info(f"Parsed poll_data: {value}")
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"JSON parse error: {e}")
                raise serializers.ValidationError(f"Invalid JSON format for poll_data: {e}")
        
        # Validate required fields
        if not isinstance(value, dict):
            raise serializers.ValidationError("Poll data must be a valid JSON object")
            
        if 'question' not in value or 'options' not in value:
            logger.error(f"poll_data missing required fields: {value}")
            raise serializers.ValidationError("Poll data must contain 'question' and 'options'")
        
        question = value['question'].strip()
        if not question:
            raise serializers.ValidationError("Poll question cannot be empty")
        
        options = value['options']
        if not isinstance(options, list) or len(options) < 2:
            raise serializers.ValidationError("Poll must have at least 2 options")
        
        # Clean and validate options
        cleaned_options = [opt.strip() for opt in options if opt.strip()]
        if len(cleaned_options) < 2:
            raise serializers.ValidationError("Poll must have at least 2 valid options")
        
        result = {
            'question': question,
            'options': cleaned_options
        }
        logger.info(f"Validated poll_data: {result}")
        return result
    
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
        """Create post with files and poll"""
        import logging
        logger = logging.getLogger(__name__)
        
        files_data = validated_data.pop('files', [])
        poll_data = validated_data.pop('poll_data', None)
        
        logger.info(f"Creating post with poll_data: {poll_data}")
        
        post = FeedPost.objects.create(**validated_data)
        
        # Create file attachments
        for file_data in files_data:
            # Determine file type based on file extension or content type
            file_type = self._determine_file_type(file_data)
            
            PostFile.objects.create(
                post=post,
                file=file_data,
                file_type=file_type,
                file_size=file_data.size,
                original_filename=file_data.name
            )
        
        # Create poll if provided
        if poll_data:
            logger.info(f"Creating poll with question: {poll_data['question']}")
            logger.info(f"Poll options: {poll_data['options']}")
            
            poll = Poll.objects.create(
                question=poll_data['question']
            )
            
            logger.info(f"Poll created with ID: {poll.id}")
            
            # Create poll options
            for index, option_text in enumerate(poll_data['options']):
                from apps.feeds.domain.entities.poll import PollOption
                option = PollOption.objects.create(
                    poll=poll,
                    text=option_text,
                    order=index
                )
                logger.info(f"Created poll option {index}: {option_text}")
            
            # Associate poll with post
            post.poll = poll
            post.save(update_fields=['poll'])
            logger.info(f"Associated poll {poll.id} with post {post.id}")
        else:
            logger.info("No poll_data provided")
        
        return post
    
    def _determine_file_type(self, file):
        """Determine file type based on extension and content type"""
        import mimetypes
        
        filename = file.name.lower()
        content_type = file.content_type if hasattr(file, 'content_type') else None
        
        # Check by MIME type first
        if content_type:
            if content_type.startswith('image/'):
                return 'image'
            elif content_type.startswith('video/'):
                return 'video'
            elif content_type.startswith('audio/'):
                return 'audio'
        
        # Check by file extension
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
            return 'image'
        elif filename.endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm')):
            return 'video'
        elif filename.endswith(('.mp3', '.wav', '.ogg', '.m4a', '.aac')):
            return 'audio'
        elif filename.endswith(('.pdf', '.doc', '.docx', '.txt', '.rtf')):
            return 'document'
        
        return 'other'


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
            parent_comment=None,
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
