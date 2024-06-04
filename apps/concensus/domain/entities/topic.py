from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=100)
    group=models.ForeignKey('Group', on_delete=models.CASCADE)

    def __str__(self):
        return self.name