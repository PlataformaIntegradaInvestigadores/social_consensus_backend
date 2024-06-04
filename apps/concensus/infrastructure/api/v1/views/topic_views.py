from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.concensus.domain.entities.topic import Topic
from apps.concensus.infrastructure.api.v1.serializers.topic_serializer import TopicSerializer

class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    permission_classes = [permissions.AllowAny]

    """ def destroy(self, request, *args, **kwargs):
        return Response({'message':'custom'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
     """
    @swagger_auto_schema(description='List of topics for a group', manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_QUERY, description="Group ID", type=openapi.TYPE_STRING)
    
    ])
    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get('group_id')
        topics = Topic.objects.filter(group__id=group_id)
        serializer = TopicSerializer(topics, many=True).data
        return Response({'data':serializer},status=status.HTTP_405_METHOD_NOT_ALLOWED)