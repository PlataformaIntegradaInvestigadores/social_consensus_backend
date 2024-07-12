# models.py
from django.db import models
from django.conf import settings

class FinalTopicOrder(models.Model):
    id = models.AutoField(primary_key=True)
    idGroup = models.ForeignKey('custom_auth.Group', on_delete=models.CASCADE)
    idUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    idTopic = models.ForeignKey('concensus.RecommendedTopic', on_delete=models.CASCADE)
    posFinal = models.IntegerField()
    label = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('idGroup', 'idUser', 'idTopic')

    def __str__(self):
        return f'Group {self.idGroup}, User {self.idUser}, Topic {self.idTopic}, Position {self.posFinal}'
