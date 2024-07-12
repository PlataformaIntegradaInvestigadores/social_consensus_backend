from django.db import models
from django.conf import settings

from apps.concensus.domain.entities.topic import RecommendedTopic

class UserExpertise(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey('custom_auth.Group', on_delete=models.CASCADE)
    topic = models.ForeignKey(RecommendedTopic, on_delete=models.CASCADE)
    expertise_level = models.IntegerField(default=1)
    has_provided_expertise = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'group', 'topic')

    def __str__(self):
        return f"{self.user.username} - {self.topic.topic_name} - {self.expertise_level}"
    
#select * from "concensus_userexpertise";