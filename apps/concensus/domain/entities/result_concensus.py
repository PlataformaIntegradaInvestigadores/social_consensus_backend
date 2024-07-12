from django.db import models

from apps.concensus.domain.entities.topic import RecommendedTopic
from apps.custom_auth.domain.entities.group import Group

class ConsensusResult(models.Model):
    idGroup = models.ForeignKey(Group, on_delete=models.CASCADE)
    idTopic = models.ForeignKey(RecommendedTopic, on_delete=models.CASCADE)
    final_value = models.FloatField()

#select * from concensus_consensusresult;