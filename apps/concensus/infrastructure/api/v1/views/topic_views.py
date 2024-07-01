import random
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from django.apps import apps 
from apps.concensus.domain.entities.topic import RecommendedTopic, Topic, TopicAddedUser
from apps.concensus.infrastructure.api.v1.serializers.topic_serializer import RecommendedTopicSerializer, TopicAddedUserSerializer, TopicSerializer
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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

""" Devuelve un json con 5 temas aleatorios que no estén asignados a ningún grupo y
 asigna el id del grupo a los topics y los guarda en la base de datos """
class RandomRecommendedTopicView(generics.ListAPIView):
    serializer_class = RecommendedTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RecommendedTopic.objects.filter(group__isnull=True)
        return random.sample(list(queryset), min(len(queryset), 5))

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        group_id = self.kwargs.get('group_id')
        if group_id:
            for topic in response.data:
                RecommendedTopic.objects.filter(id=topic['id']).update(group_id=group_id)
        return response

""" Devuelve los topics de un grupo por su id de grupo """
class RecommendedTopicsByGroupView(generics.ListAPIView):
    serializer_class = RecommendedTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return RecommendedTopic.objects.filter(group_id=group_id)

""" Devuelve los topics añadidos por un usuario al grupo por su id de grupo """
class TopicsAddedByGroupView(generics.ListAPIView):
    serializer_class = TopicAddedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return TopicAddedUser.objects.filter(group_id=group_id)

""" Devuelve los topics recomendados y añadidos por un usuario al grupo por su id de grupo"""
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

""" Para agregar nuevos temas a la BD que luego disparará la notificación por WebSocket """
class AddTopicView(APIView):
    def post(self, request, group_id):
        data = request.data
        topic_name = data.get('topic')
        user_id = data.get('user_id')
        
        if not topic_name or not user_id:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        RecommendedTopic = apps.get_model('concensus', 'RecommendedTopic')
        TopicAddedUser = apps.get_model('concensus', 'TopicAddedUser')
        
       # Verificar si el tópico ya existe en RecommendedTopic para el grupo específico
        existing_recommended_topic = RecommendedTopic.objects.filter(topic_name=topic_name, group_id=group_id).first()
        if existing_recommended_topic:
            # Verificar si ya se ha añadido este tópico en TopicAddedUser para el grupo específico
            existing_topic_added_user = TopicAddedUser.objects.filter(topic=existing_recommended_topic, group_id=group_id).first()
            if existing_topic_added_user:
                return Response({"error": "Topic already exists in this group"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                topic_added = TopicAddedUser.objects.create(
                    topic=existing_recommended_topic, group_id=group_id, user_id=user_id
                )
        else:
            # Crear el tópico en RecommendedTopic ya que no existe en este grupo
            recommended_topic = RecommendedTopic.objects.create(topic_name=topic_name, group_id=group_id)
            topic_added = TopicAddedUser.objects.create(
                topic=recommended_topic, group_id=group_id, user_id=user_id
            )

        serializer = TopicAddedUserSerializer(topic_added)

        # Enviar notificación por WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'group_{group_id}',
            {
                'type': 'group_message',
                'message': {
                    'type': 'new_topic',
                    'id': topic_added.id,
                    'topic_name': topic_added.topic.topic_name,
                    'user_id': topic_added.user_id,
                    'group_id': topic_added.group_id,
                    'added_at': topic_added.added_at.isoformat()
                }
            }
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


#select * from "concensus_recommendedtopic";
#select * from "concensus_topicaddeduser";

    #TRUNCATE TABLE "concensus_recommendedtopic" CASCADE;
    #TRUNCATE TABLE "concensus_topicaddeduser" CASCADE;