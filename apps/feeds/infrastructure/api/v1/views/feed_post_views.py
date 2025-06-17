from rest_framework import generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.feeds.domain.entities.feed_post import FeedPost
from apps.feeds.domain.entities.post_file import PostFile
from apps.feeds.domain.services.feed_service import FeedService
from apps.feeds.infrastructure.api.v1.serializers.feed_post_serializers import (
    FeedPostSerializer,
    FeedPostCreateSerializer,
    FeedPostDetailSerializer,
    PostFileSerializer,
)


class FeedPostListCreateView(generics.ListCreateAPIView):
    """
    List and create feed posts
    
    GET: List user's posts
    POST: Create new post
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's posts"""
        return FeedPost.objects.filter(
            author=self.request.user
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FeedPostCreateSerializer
        return FeedPostSerializer
    
    def perform_create(self, serializer):
        """Create post with author and embedding"""
        with transaction.atomic():
            # Set author
            serializer.validated_data['author'] = self.request.user
            
            # Create post using service
            feed_service = FeedService()
            post = feed_service.create_post(
                author=self.request.user,
                content=serializer.validated_data['content'],
                files=serializer.validated_data.get('files', []),
                tags=serializer.validated_data.get('tags', []),
                is_public=serializer.validated_data.get('is_public', True)
            )
            
            # Update serializer instance for response
            serializer.instance = post


class FeedPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a feed post
    
    GET: Get post details
    PUT/PATCH: Update post (author only)
    DELETE: Delete post (author only)
    """
    serializer_class = FeedPostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FeedPost.objects.select_related('author').prefetch_related('files', 'comments')
    
    def get_object(self):
        """Get post and record view interaction"""
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        
        # Record view interaction if GET request
        if self.request.method == 'GET':
            feed_service = FeedService()
            feed_service.handle_user_interaction(
                user=self.request.user,
                post=obj,
                interaction_type='view'
            )
        
        return obj
    
    def perform_update(self, serializer):
        """Update post (author only)"""
        if serializer.instance.author != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own posts")
        
        # Update embedding if content changed
        if 'content' in serializer.validated_data:
            feed_service = FeedService()
            post = serializer.save()
            feed_service._update_post_embedding(post)
    
    def perform_destroy(self, instance):
        """Delete post (author only)"""
        if instance.author != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own posts")
        instance.delete()


class FeedPostFileUploadView(generics.CreateAPIView):
    """
    Upload additional files to existing post
    
    POST: Add files to post
    """
    serializer_class = PostFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        """Add files to existing post"""
        post_id = kwargs.get('post_id')
        post = get_object_or_404(FeedPost, id=post_id)
        
        # Check ownership
        if post.author != request.user:
            return Response(
                {"error": "You can only add files to your own posts"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check file limit
        current_files = post.files.count()
        new_files = request.FILES.getlist('files', [])
        
        if current_files + len(new_files) > 10:
            return Response(
                {"error": "Cannot have more than 10 files per post"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create file attachments
        created_files = []
        for file in new_files:
            file_obj = PostFile.objects.create(post=post, file=file)
            created_files.append(file_obj)
        
        serializer = self.get_serializer(created_files, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FeedPostSearchView(generics.ListAPIView):
    """
    Search feed posts
    
    GET: Search posts by content, tags, author
    """
    serializer_class = FeedPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Search posts"""
        queryset = FeedPost.objects.filter(is_public=True)
        
        # Search parameters
        query = self.request.query_params.get('q', '')
        tags = self.request.query_params.getlist('tags', [])
        author = self.request.query_params.get('author', '')
        
        if query:
            queryset = queryset.filter(content__icontains=query)
        
        if tags:
            queryset = queryset.filter(tags__overlap=tags)
        
        if author:
            queryset = queryset.filter(author__username__icontains=author)
        
        return queryset.order_by('-created_at')


class FeedPostStatsView(generics.RetrieveAPIView):
    """
    Get post statistics
    
    GET: Get detailed post stats
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        """Get post statistics"""
        post_id = kwargs.get('pk')
        post = get_object_or_404(FeedPost, id=post_id)
        
        # Check if user can view stats (author only for now)
        if post.author != request.user:
            return Response(
                {"error": "You can only view stats for your own posts"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'post_id': post.id,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'views_count': post.views_count,
            'shares_count': post.shares_count,
            'engagement_score': post.engagement_score,
            'files_count': post.files.count(),
            'created_at': post.created_at,
            'last_interaction': post.metadata.get('last_interaction'),
        }
        
        return Response(stats)
