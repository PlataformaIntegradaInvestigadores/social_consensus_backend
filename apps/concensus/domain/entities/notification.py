from django.db import models

from apps.custom_auth.domain.entities.group import Group
from apps.custom_auth.domain.entities.user import User

class NotificationPhaseOne(models.Model):
    NOTIFICATION_TYPES = (
        ('new_topic', 'New Topic'),
        ('topic_visited', 'Topic Visited'),
        ('consensus_completed', 'Consensus Completed'),
        ('combined_search', 'Combined Search'),
        ('user_expertise', 'User Expertise'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.notification_type}'
    

""" 

TABLA NOTIFICATION_PHASE_ONE

id	|user_id |group_id	|notification_type	|message	                     |created_at	        
----------------------------------------------------------------------------------------------------
1	12345	 67890	    new_topic	        Ricardo Díaz 📥 added Topic 6	 2024-07-01 10:00:00	
2	67891	 12345	    topic_visited	    Carlos Gómez 👀 visited Topic 1	 2024-07-01 10:05:00	

 """

#concensus_notificationphaseone 
#select * from "concensus_notificationphaseone";

#TRUNCATE TABLE "concensus_notificationphaseone" CASCADE;

