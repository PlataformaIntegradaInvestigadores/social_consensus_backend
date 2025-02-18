from django.db import models
from apps.custom_auth.domain.entities.group import Group
from django.utils.timezone import now

class Debate(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='debates')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DurationField()
    is_closed = models.BooleanField(default=False)



    def __str__(self):
        return f"{self.title} - {self.group.title}"

    class Meta:
         db_table = 'debates'



    def is_time_exceeded(self):
        """
        Comprueba si el tiempo del debate ha expirado.
        """
        return now() >= self.get_closing_time()

    def get_closing_time(self):
        """
        Calcula la fecha y hora exacta en que debe cerrarse el debate.
        """
        return self.created_at + self.end_time