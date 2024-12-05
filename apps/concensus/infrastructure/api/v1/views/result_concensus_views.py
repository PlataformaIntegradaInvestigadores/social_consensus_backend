import logging
from django.apps import apps
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from apps.concensus.domain.entities.user_phase import UserPhase

logger = logging.getLogger(__name__)


class ExecuteConsensusCalculationsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, group_id):
        Group = apps.get_model('custom_auth', 'Group')
        User = apps.get_model('custom_auth', 'User')
        RecommendedTopic = apps.get_model('concensus', 'RecommendedTopic')
        FinalTopicOrder = apps.get_model('concensus', 'FinalTopicOrder')
        ConsensusResult = apps.get_model('concensus', 'ConsensusResult')
        UserExpertise = apps.get_model('concensus', 'UserExpertise')

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if all users have completed phase 1 and 2
        users_in_group = UserPhase.objects.filter(group=group, phase=2).values_list('user', flat=True)
        total_users = UserPhase.objects.filter(group=group).values_list('user', flat=True).distinct().count()

        logger.info(f'Users in group: {users_in_group}')
        logger.info(f'Total users in group: {total_users}')

        if len(users_in_group) != total_users:
            return Response({"error": "Not all users have completed phase 1 and 2"}, status=status.HTTP_400_BAD_REQUEST)

        # Get all topics for the group
        topics = RecommendedTopic.objects.filter(group=group).order_by('topic_name')

        # Prepare data structures
        topic_names = [topic.topic_name for topic in topics]
        user_ids = list(users_in_group)

        # Initialize positions and expertise data
        positions_data = {topic_name: {} for topic_name in topic_names}
        expertise_data = {topic_name: {} for topic_name in topic_names}
        labels_data = {topic_name: [] for topic_name in topic_names}

        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            user_positions = FinalTopicOrder.objects.filter(idUser=user, idGroup=group)
            user_expertise = UserExpertise.objects.filter(user=user, group=group)

            for pos in user_positions:
                topic_name = pos.idTopic.topic_name
                positions_data[topic_name][user.username] = pos.posFinal
                if pos.label:
                    labels_data[topic_name].append(f"{user.first_name} {user.last_name} rated it as {pos.label}")
            for exp in user_expertise:
                topic_name = exp.topic.topic_name
                expertise_data[topic_name][user.username] = exp.expertise_level

        # Default expertise level is 1 if not specified
        for topic_name in topic_names:
            for user in user_ids:
                username = User.objects.get(id=user).username
                if username not in expertise_data[topic_name]:
                    expertise_data[topic_name][username] = 1

        # TODO: Implement the consensus calculation algorithm
        print(positions_data)
        # Calculate the weighted rankings
        weighted_rankings = {}
        for topic_name in topic_names:
            total_weighted_score = 0
            total_expertise = 0
            for user in user_ids:
                username = User.objects.get(id=user).username
                pos = positions_data[topic_name].get(username, 0)
                exp = expertise_data[topic_name].get(username, 1)
                total_weighted_score += pos * exp
                total_expertise += exp

            if total_expertise > 0:
                weighted_rankings[topic_name] = total_weighted_score / total_expertise
            else:
                weighted_rankings[topic_name] = 0

        sorted_rankings = sorted(weighted_rankings.items(), key=lambda x: x[1], reverse=True)

        # Store results in the database
        ConsensusResult.objects.filter(idGroup=group).delete()  # Clear previous results
        results = []
        for topic_name, final_value in sorted_rankings:
            topic = topics.get(topic_name=topic_name)
            ConsensusResult.objects.create(idGroup=group, idTopic=topic, final_value=final_value)
            labels = labels_data[topic_name] if labels_data[topic_name] else ["There aren't labels"]
            results.append({
                "id_topic": topic.id,
                "topic_name": topic_name,
                "final_value": final_value,
                "labels": labels
            })
            logger.info(f'Saved Consensus Result - Topic: {topic_name}, Value: {final_value}, Labels: {labels}')

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'phase3_group_{group_id}',
            {
                'type': 'group_message',
                'message': {
                    'type': 'consensus_calculation_completed',
                    'group_id': group_id,
                    'notification_message': 'Consensus phase 3 calculations completed.',
                    'results': results
                }
            }
        )
        logger.info(f'WebSocket notification sent for group: {group_id} with results: {results}')

        return Response({"message": "Consensus calculations completed.", "results": results}, status=status.HTTP_200_OK)