import logging
import random
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from rest_framework import status
from django.apps import apps
from apps.concensus.domain.entities.topic import RecommendedTopic, Topic, TopicAddedUser
from apps.concensus.domain.entities.final_topic_order import FinalTopicOrder
from apps.concensus.domain.entities.notification import NotificationPhaseOne
from apps.concensus.infrastructure.api.v1.serializers.final_topic_serializer import FinalTopicOrderSerializer
from apps.concensus.infrastructure.api.v1.serializers.topic_serializer import RecommendedTopicSerializer, \
    TopicAddedUserSerializer, TopicSerializer
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    permission_classes = [permissions.AllowAny]

    """ def destroy(self, request, *args, **kwargs):
        return Response({'message':'custom'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
     """

    @extend_schema(
        description="List of topics for a group",
        parameters=[
            OpenApiParameter(
                name="group_id",
                location=OpenApiParameter.QUERY,
                description="Group ID",
                required=True,
                type=str
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get('group_id')
        topics = Topic.objects.filter(group__id=group_id)
        serializer = TopicSerializer(topics, many=True).data
        return Response({'data': serializer}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

""" Devuelve un json con 5 temas aleatorios que no estén asignados a ningún grupo y
 asigna el id del grupo a los topics y los guarda en la base de datos """
class RandomRecommendedTopicView(generics.ListAPIView):
    serializer_class = RecommendedTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RecommendedTopic.objects.filter(group__isnull=True)
        sampled_queryset = random.sample(list(queryset), min(len(queryset), 5))
        return sorted(sampled_queryset, key=lambda topic: topic.topic_name)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        group_id = self.kwargs.get('group_id')
        if group_id:
            for topic in response.data:
                RecommendedTopic.objects.filter(id=topic['id']).update(group_id=group_id)
        return response

""" Devuelve los topics de un grupo por su id de grupo EN ORDEN ALFABÉTICO"""
class RecommendedTopicsByGroupView(generics.ListAPIView):
    serializer_class = RecommendedTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return RecommendedTopic.objects.filter(group_id=group_id).order_by('topic_name')


""" Devuelve los topics con la votación realizada por el usuario """
class FinalTopicsVotedByUserView(generics.ListAPIView):
    serializer_class = FinalTopicOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Final topics voted by user",
        description="List of final topics voted by user",
        responses={
            200: OpenApiResponse(
                description="List of final topics voted by the user",
                response=dict,  # Usamos dict porque el retorno es un diccionario JSON
                examples=[
                    OpenApiExample(
                        name="Final topics voted by user",
                        value={
                            "data": [
                                {
                                    "id": 67,
                                    "topic_name": "Bioinformatics and Genomic Data Analysis",
                                    "posFinal": 5,
                                    "tags": [
                                        "Novel"
                                    ]
                                },
                                {
                                    "id": 179,
                                    "topic_name": "AI in Employee Performance Management",
                                    "posFinal": 4,
                                    "tags": [
                                        "Attractive"
                                    ]
                                },
                                {
                                    "id": 124,
                                    "topic_name": "AI in Sports Performance Analysis",
                                    "posFinal": 3,
                                    "tags": [
                                        "Unfamiliar"
                                    ]
                                },
                                {
                                    "id": 157,
                                    "topic_name": "Machine Learning in Financial Fraud Detection",
                                    "posFinal": 2,
                                    "tags": []
                                },
                                {
                                    "id": 36,
                                    "topic_name": "AI in Talent Acquisition",
                                    "posFinal": 1,
                                    "tags": [
                                        "Obsolete"
                                    ]
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )
    def list(self, request, *args, **kwargs):
        user = self.request.user
        group_id = self.kwargs['group_id']

        final_topics = FinalTopicOrder.objects.filter(idGroup=group_id, idUser=user.id).order_by('-posFinal')
        final_topics_serializer = FinalTopicOrderSerializer(final_topics, many=True)

        results = []

        for topic in final_topics_serializer.data:
            topic_id = topic['idTopic']
            topic_name = RecommendedTopic.objects.get(id=topic_id).topic_name

            # Procesamos los tags
            labels = topic['label']
            if labels:
                tags = [tag.strip() for tag in labels.split(',')] if ',' in labels else [labels]
            else:
                tags = []

            results.append({
                'id': topic_id,
                'topic_name': topic_name,
                'posFinal': topic['posFinal'],
                'tags': tags
            })

        return Response({
            'data': results
        })

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
""" El endpoint REST se encargará de validar los datos, agregar el topic, crear la notificación y enviar el mensaje por WebSocket. """
class AddTopicView(APIView):
    def post(self, request, group_id):
        data = request.data
        topic_name = data.get('topic')
        user_id = data.get('user_id')

        if not topic_name or not user_id:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar la fase de todos los usuarios en el grupo
        UserPhase = apps.get_model('concensus', 'UserPhase')
        users_in_phase_two_or_higher = UserPhase.objects.filter(group_id=group_id, phase__gte=1).exists()

        if users_in_phase_two_or_higher:
            return Response({"error": "A user in this group is already in phase 2, adding new topics is not allowed."},
                            status=status.HTTP_403_FORBIDDEN)

        RecommendedTopic = apps.get_model('concensus', 'RecommendedTopic')
        TopicAddedUser = apps.get_model('concensus', 'TopicAddedUser')
        User = apps.get_model('custom_auth', 'User')
        Group = apps.get_model('custom_auth', 'Group')

        # Verificar si el usuario ya ha añadido un tópico en este grupo
        user_topic_count = TopicAddedUser.objects.filter(group_id=group_id, user_id=user_id).count()
        if user_topic_count > 0:
            return Response({"error": "You can only add one topic per group"}, status=status.HTTP_403_FORBIDDEN)

        # Verificar si el tópico ya existe en RecommendedTopic para el grupo específico
        existing_recommended_topic = RecommendedTopic.objects.filter(topic_name=topic_name, group_id=group_id).first()

        if existing_recommended_topic:
            # Verificar si ya se ha añadido este tópico en TopicAddedUser para el grupo específico
            existing_topic_added_user = TopicAddedUser.objects.filter(topic=existing_recommended_topic,
                                                                      group_id=group_id).first()
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

        # Crear notificación
        user = User.objects.get(id=user_id)
        group = Group.objects.get(id=group_id)
        message = f'{user.first_name} {user.last_name} 📥 added topic <i>{topic_name}</i>'
        NotificationPhaseOne.objects.create(
            user=user,
            group=group,
            notification_type='new_topic',
            message=message
        )

        # Construir la URL completa de la imagen de perfil
        profile_picture_url = user.profile_picture.url if user.profile_picture else None

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
                    'added_at': topic_added.added_at.isoformat(),
                    'notification_message': message,
                    'profile_picture_url': profile_picture_url,
                }
            }
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
