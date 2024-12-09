from django.db import models
from .debate import Debate
from .message import DebateMessage


class DebateSummary(models.Model):
    id = models.AutoField(primary_key=True)
    idDebate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='summaries')
    summaryText = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debate_summaries'

    def __str__(self):
        return f'Summary for Debate {self.idDebate}'


class SummaryMessage(models.Model):
    id = models.AutoField(primary_key=True)
    idSummary = models.ForeignKey(DebateSummary, on_delete=models.CASCADE, related_name='messages')
    idMessage = models.ForeignKey(DebateMessage, on_delete=models.CASCADE, related_name='summary_links')

    class Meta:
        db_table = 'summary_messages'

    def __str__(self):
        return f'Summary {self.idSummary.id} includes Message {self.idMessage.id}'
