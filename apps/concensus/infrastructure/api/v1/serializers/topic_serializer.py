from rest_framework import serializers

from apps.concensus.domain.entities.topic import Topic

class TopicSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['id','name','group_name']

    def get_group_name(self, obj):
        return obj.group.name