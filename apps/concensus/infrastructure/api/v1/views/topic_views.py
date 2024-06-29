import random
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.concensus.domain.entities.topic import RecommendedTopic, Topic, TopicAddedUser
from apps.concensus.infrastructure.api.v1.serializers.topic_serializer import RecommendedTopicSerializer, TopicAddedUserSerializer, TopicSerializer

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

""" Devuelve un json con 10 temas aleatorios que no estén asignados a ningún grupo y
 asigna el id del grupo a los topics y los guarda en la base de datos """
class RandomRecommendedTopicView(generics.ListAPIView):
    serializer_class = RecommendedTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RecommendedTopic.objects.filter(group__isnull=True)
        return random.sample(list(queryset), min(len(queryset), 10))

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        group_id = self.kwargs.get('group_id')
        if group_id:
            for topic in response.data:
                RecommendedTopic.objects.filter(id=topic['id']).update(group_id=group_id)
        return response

class RecommendedTopicsByGroupView(generics.ListAPIView):
    serializer_class = RecommendedTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return RecommendedTopic.objects.filter(group_id=group_id)

class TopicsAddedByGroupView(generics.ListAPIView):
    serializer_class = TopicAddedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return TopicAddedUser.objects.filter(group_id=group_id)

class GroupTopicsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        group_id = self.kwargs['group_id']
        recommended_topics = RecommendedTopic.objects.filter(group_id=group_id)
        added_topics = TopicAddedUser.objects.filter(group_id=group_id)

        recommended_serializer = RecommendedTopicSerializer(recommended_topics, many=True)
        added_serializer = TopicAddedUserSerializer(added_topics, many=True)

        return Response({
            'recommended_topics': recommended_serializer.data,
            'added_topics': added_serializer.data
        })