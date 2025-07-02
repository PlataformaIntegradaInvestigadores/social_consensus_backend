from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes as perm_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import models

from apps.feeds.domain.entities.feed_post import FeedPost
from apps.feeds.domain.services.feed_service import FeedService
from apps.feeds.infrastructure.api.v1.serializers.feed_serializers import (
    FeedSerializer,
    FeedRequestSerializer,
    UserInteractionSerializer,
    FeedFilterSerializer,
)
from apps.feeds.infrastructure.api.v1.serializers.feed_post_serializers import (
    FeedPostSerializer,
    FeedPostDetailSerializer,
)


class FeedView(generics.GenericAPIView):
    """
    Get personalized or trending feed
    
    GET: Get feed based on type (personalized, trending, latest)
    POST: Get feed with filters
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get feed"""
        # Parse query parameters
        serializer = FeedRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        feed_type = serializer.validated_data['feed_type']
        limit = serializer.validated_data['limit']
        cursor = serializer.validated_data.get('cursor')
        
        # Get feed using service
        feed_service = FeedService()
        
        if feed_type == 'personalized':
            posts, has_next, next_cursor = feed_service.get_personalized_feed(
                user=request.user,
                limit=limit,
                cursor=cursor
            )
        elif feed_type == 'trending':
            posts, has_next, next_cursor = feed_service.get_trending_feed(
                limit=limit,
                cursor=cursor
            )
        else:  # latest
            posts, has_next, next_cursor = feed_service.get_latest_feed(
                limit=limit,
                cursor=cursor
            )
        
        # Serialize response
        post_serializer = FeedPostSerializer(
            posts, 
            many=True, 
            context={'request': request}
        )
        
        response_data = {
            'posts': post_serializer.data,
            'has_next': has_next,
            'next_cursor': next_cursor,
            'total_count': len(posts)
        }
        
        return Response(response_data)
    
    def post(self, request, *args, **kwargs):
        """Get filtered feed"""
        # Parse request data
        request_serializer = FeedRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        
        filter_serializer = FeedFilterSerializer(data=request.data.get('filters', {}))
        filter_serializer.is_valid(raise_exception=True)
        
        feed_type = request_serializer.validated_data['feed_type']
        limit = request_serializer.validated_data['limit']
        cursor = request_serializer.validated_data.get('cursor')
        filters = filter_serializer.validated_data
        
        # Get filtered feed
        feed_service = FeedService()
        posts, has_next, next_cursor = feed_service.get_filtered_feed(
            user=request.user,
            feed_type=feed_type,
            filters=filters,
            limit=limit,
            cursor=cursor
        )
        
        # Serialize response
        post_serializer = FeedPostDetailSerializer(
            posts, 
            many=True, 
            context={'request': request}
        )
        
        response_data = {
            'posts': post_serializer.data,
            'has_next': has_next,
            'next_cursor': next_cursor,
            'total_count': len(posts)
        }
        
        return Response(response_data)


class UserInteractionView(generics.GenericAPIView):
    """
    Record user interactions with posts
    
    POST: Record interaction (view, share, click, save)
    """
    serializer_class = UserInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Record user interaction"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        post_id = serializer.validated_data['post_id']
        interaction_type = serializer.validated_data['interaction_type']
        metadata = serializer.validated_data['metadata']
        
        # Get post
        post = get_object_or_404(FeedPost, id=post_id)
        
        # Record interaction using service
        feed_service = FeedService()
        feed_service.handle_user_interaction(
            user=request.user,
            post=post,
            interaction_type=interaction_type,
            metadata=metadata
        )
        
        return Response({
            'message': f'{interaction_type.title()} recorded successfully',
            'post_id': post_id,
            'interaction_type': interaction_type
        })


@api_view(['GET'])
@perm_classes([permissions.IsAuthenticated])
def trending_posts(request):
    """
    Get trending posts
    
    GET: Get trending posts based on engagement
    """
    # Get parameters
    limit = min(int(request.GET.get('limit', 20)), 50)
    time_range = request.GET.get('time_range', '24h')  # 24h, 7d, 30d
    
    # Calculate time threshold
    now = timezone.now()
    if time_range == '24h':
        time_threshold = now - timezone.timedelta(hours=24)
    elif time_range == '7d':
        time_threshold = now - timezone.timedelta(days=7)
    elif time_range == '30d':
        time_threshold = now - timezone.timedelta(days=30)
    else:
        time_threshold = now - timezone.timedelta(hours=24)
    
    # Get trending posts
    posts = FeedPost.objects.filter(
        created_at__gte=time_threshold,
        is_public=True
    ).order_by('-engagement_score', '-created_at')[:limit]
    
    # Serialize
    serializer = FeedPostDetailSerializer(posts, many=True, context={'request': request})
    
    return Response({
        'posts': serializer.data,
        'time_range': time_range,
        'total_count': len(posts)
    })


@api_view(['GET'])
@perm_classes([permissions.IsAuthenticated])
def user_feed_stats(request):
    """
    Get user's feed statistics
    
    GET: Get user's posting and engagement stats
    """
    user = request.user
    
    # Get user's posts
    user_posts = FeedPost.objects.filter(author=user)
    
    # Calculate stats
    stats = {
        'total_posts': user_posts.count(),
        'total_likes_received': sum(post.likes_count for post in user_posts),
        'total_comments_received': sum(post.comments_count for post in user_posts),
        'total_views_received': sum(post.views_count for post in user_posts),
        'total_shares_received': sum(post.shares_count for post in user_posts),
        'average_engagement': user_posts.aggregate(
            avg_engagement=models.Avg('engagement_score')
        )['avg_engagement'] or 0,
        'most_liked_post': None,
        'most_commented_post': None,
    }
    
    # Get most liked and commented posts
    most_liked = user_posts.order_by('-likes_count').first()
    most_commented = user_posts.order_by('-comments_count').first()
    
    if most_liked:
        stats['most_liked_post'] = {
            'id': most_liked.id,
            'content': most_liked.content[:100],
            'likes_count': most_liked.likes_count
        }
    
    if most_commented:
        stats['most_commented_post'] = {
            'id': most_commented.id,
            'content': most_commented.content[:100],
            'comments_count': most_commented.comments_count
        }
    
    return Response(stats)


@api_view(['GET'])
@perm_classes([permissions.IsAuthenticated])
def feed_recommendations(request):
    """
    Get personalized feed recommendations
    
    GET: Get posts recommended based on user embeddings
    """
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    # Get recommendations using service
    feed_service = FeedService()
    posts, has_next, next_cursor = feed_service.get_personalized_feed(
        user=request.user,
        limit=limit
    )
    
    # Serialize
    serializer = FeedPostDetailSerializer(
        posts, 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'recommendations': serializer.data,
        'has_next': has_next,
        'next_cursor': next_cursor,
        'total_count': len(posts)
    })


class UserPostsView(generics.ListAPIView):
    """
    Get posts from the current authenticated user
    
    GET: Get user's own posts with pagination and filters
    """
    serializer_class = FeedPostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get current user's posts"""
        user = self.request.user
        queryset = FeedPost.objects.filter(
            author=user
        ).select_related('author').prefetch_related(
            'post_files', 'comments'
        ).order_by('-created_at')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List user posts with pagination"""
        queryset = self.get_queryset()
        
        # Parse pagination parameters
        limit = min(int(request.GET.get('limit', 20)), 50)
        cursor = request.GET.get('cursor')
        
        # Apply cursor pagination if provided
        if cursor:
            try:
                from datetime import datetime
                cursor_date = datetime.fromisoformat(cursor.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__lt=cursor_date)
            except (ValueError, TypeError):
                pass  # Invalid cursor, ignore
        
        # Get posts with limit + 1 to check if there's a next page
        posts = list(queryset[:limit + 1])
        has_next = len(posts) > limit
        
        if has_next:
            posts = posts[:limit]
        
        # Get next cursor
        next_cursor = None
        if has_next and posts:
            next_cursor = posts[-1].created_at.isoformat()
        
        # Serialize posts
        serializer = self.get_serializer(posts, many=True)
        
        # Calculate total posts count for user
        total_count = FeedPost.objects.filter(author=request.user).count()
        
        response_data = {
            'posts': serializer.data,
            'has_next': has_next,
            'next_cursor': next_cursor,
            'total_count': total_count,
            'user_info': {
                'id': str(request.user.id),
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
