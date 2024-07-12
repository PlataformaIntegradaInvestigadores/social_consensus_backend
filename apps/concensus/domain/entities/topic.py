from django.db import models

from apps.custom_auth.domain.entities.group import Group
from apps.custom_auth.domain.entities.user import User

class Topic(models.Model):
    name = models.CharField(max_length=100)
    group=models.ForeignKey('Group', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class RecommendedTopic(models.Model):
    topic_name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, related_name='recommended_topics', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.topic_name
    
class TopicAddedUser(models.Model):
    topic = models.ForeignKey(RecommendedTopic, related_name='added_by_users', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='added_topics', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='added_topics', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} added {self.topic.topic_name} to {self.group.name}"
    

#select * from "concensus_recommendedtopic";
#select * from "concensus_topicaddeduser";

    #TRUNCATE TABLE "concensus_recommendedtopic" CASCADE;
    #TRUNCATE TABLE "concensus_topicaddeduser" CASCADE;