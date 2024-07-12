from rest_framework import serializers

from apps.concensus.domain.entities.topic import RecommendedTopic, Topic, TopicAddedUser

class TopicSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['id','name','group_name']

    def get_group_name(self, obj):
        return obj.group.name

class RecommendedTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedTopic
        fields = ['id', 'topic_name', 'group']

""" Para convertir las instancias de este modelo a JSON cuando enviemos mensajes a través del WebSocket """
class TopicAddedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicAddedUser
        fields = ['id', 'topic', 'group', 'user', 'added_at']