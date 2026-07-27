from django.db import models
from apps.concensus.domain.entities.topic import Topic
from apps.concensus.domain.entities.notification import NotificationPhaseOne
from apps.concensus.domain.entities.user_expertice import UserExpertise
from apps.concensus.domain.entities.notification import NotificationPhaseTwo
from apps.concensus.domain.entities.final_topic_order import FinalTopicOrder
from apps.concensus.domain.entities.user_phase import UserPhase
from apps.concensus.domain.entities.result_concensus import ConsensusResult
from apps.concensus.domain.entities.user_satisfaction import UserSatisfaction

# Importar las entidades de jobs
from apps.jobs.domain.entities.company import Company
from apps.jobs.domain.entities.jobs import Jobs
from apps.jobs.domain.entities.postulants import Postulants
from apps.jobs.domain.entities.job_interaction import JobInteraction
