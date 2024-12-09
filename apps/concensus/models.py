from django.db import models
from apps.concensus.domain.entities.group import Group
from apps.concensus.domain.entities.topic import Topic
from apps.concensus.domain.entities.notification import NotificationPhaseOne
from apps.concensus.domain.entities.user_expertice import UserExpertise
from apps.concensus.domain.entities.notification import NotificationPhaseTwo
from apps.concensus.domain.entities.final_topic_order import FinalTopicOrder
from apps.concensus.domain.entities.user_phase import UserPhase
from apps.concensus.domain.entities.result_concensus import ConsensusResult
from apps.concensus.domain.entities.user_satisfaction import UserSatisfaction
#  CHAT GRUPAL
from apps.concensus.domain.entities.debate import Debate
from apps.concensus.domain.entities.participant import DebateParticipant
from apps.concensus.domain.entities.message import DebateMessage
from apps.concensus.domain.entities.vote import ClassificationVote
from apps.concensus.domain.entities.reaction import MessageReaction
from apps.concensus.domain.entities.thread import MessageThread
from apps.concensus.domain.entities.summary import DebateSummary, SummaryMessage
from apps.concensus.domain.entities.important_message import ImportantMessage

# Create your models here.
