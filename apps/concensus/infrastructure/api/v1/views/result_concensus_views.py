import logging
from django.apps import apps
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from collections import defaultdict
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from apps.concensus.domain.entities.user_phase import UserPhase

logger = logging.getLogger(__name__)


class ExecuteConsensusCalculationsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Execute Consensus Calculations for a Group",
        description=(
                "This endpoint triggers the execution of consensus calculations for a specific group. "
                "It validates that all users have completed the required phases before calculating the consensus "
                "based on the users' positions and expertise levels on the recommended topics."
        ),
        responses={
            200: OpenApiResponse(
                description="Consensus calculations completed successfully.",
                response=Response,
                examples=[
                    OpenApiExample(
                        name="Successful consensus calculation",
                        value={
                            "message": "Consensus calculations completed.",
                            "results": [
                                {
                                    "id_topic": 122,
                                    "topic_name": "AI in Personalized Travel Recommendations",
                                    "final_value": 4.5,
                                    "labels": ["There aren't labels"]
                                },
                                {
                                    "id_topic": 87,
                                    "topic_name": "Internet of Medical Things",
                                    "final_value": 3.5,
                                    "labels": ["There aren't labels"]
                                },
                                {
                                    "id_topic": 78,
                                    "topic_name": "AI in Autonomous Logistics",
                                    "final_value": 3.0,
                                    "labels": ["There aren't labels"]
                                },
                                {
                                    "id_topic": 74,
                                    "topic_name": "AI-Driven Supply Chain Optimization",
                                    "final_value": 2.5,
                                    "labels": ["There aren't labels"]
                                },
                                {
                                    "id_topic": 194,
                                    "topic_name": "AI in Smart Building Management",
                                    "final_value": 1.5,
                                    "labels": ["There aren't labels"]
                                }
                            ]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Not all users have completed phase 1 and 2.",
                response=Response,
                examples=[
                    OpenApiExample(
                        name="Incomplete phases",
                        value={"error": 'Not all users have completed phase 1 and 2'}
                    )
                ]
            ),
            404: OpenApiResponse(
                description="The specified group does not exist.",
                response=Response,
                examples=[
                    OpenApiExample(
                        name="Group not found",
                        value={"error": "Group does not exist"}
                    )
                ]
            )
        }
    )
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
        total_users = group.users.count()

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

        # Implement the consensus calculation algorithm
        voting_type = group.voting_type
        sorted_rankings = []

        if voting_type == 'Positional Voting':
            sorted_rankings = self.calculate_positional_voting(topic_names, user_ids, positions_data, expertise_data)
        if voting_type == 'Non-Positional Voting':
            sorted_rankings = self.schulze_voting_algorithm(positions_data, topic_names)

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
        async_to_sync(channel_layer.group_send)(f'phase3_group_{group_id}', {
            'type': 'group_message',
            'message': {
                'type': 'consensus_calculation_completed',
                'group_id': group_id,
                'notification_message': 'Consensus phase 3 calculations completed.',
                'results': results
            }
        })
        logger.info(f'WebSocket notification sent for group: {group_id} with results: {results}')

        return Response({"message": "Consensus calculations completed.", "results": results}, status=status.HTTP_200_OK)

    def schulze_voting_algorithm(self, positions_data, topic_names):
        """
         Calculate the ranking of topics using the Schulze Voting algorithm.

        Parameters:
        - positions_data (dict): Dictionary mapping topic names to user positions.
        - topic_names (list): List of topic names to evaluate.

        Returns:
        - sorted_topics (list): List of tuples containing topics and their total strength, sorted in descending order of strength.
        """
        # Crear matriz de comparación por pares P
        P = defaultdict(lambda: defaultdict(int))

        # Llenar la matriz de comparación por pares
        for topic_name in topic_names:
            for other_topic_name in topic_names:
                if topic_name != other_topic_name:
                    for user, pos in positions_data[topic_name].items():
                        other_pos = positions_data[other_topic_name].get(user, float('-inf'))  # Invertir prioridad
                        if pos > other_pos:  # Valor más alto significa mayor preferencia
                            P[topic_name][other_topic_name] += 1
                        elif pos < other_pos:
                            P[other_topic_name][topic_name] += 1

        # Inicializar la matriz de fortalezas de caminos S
        S = defaultdict(lambda: defaultdict(int))
        for i in topic_names:
            for j in topic_names:
                if i != j:
                    if P[i][j] > P[j][i]:
                        S[i][j] = P[i][j]
                    else:
                        S[i][j] = 0

        # Algoritmo de Floyd-Warshall para calcular las fortalezas de caminos
        for k in topic_names:
            for i in topic_names:
                for j in topic_names:
                    if i != j and i != k and j != k:
                        S[i][j] = max(S[i][j], min(S[i][k], S[k][j]))

        # Crear lista de fortalezas totales para cada tema
        topic_strength = []
        for topic_name in topic_names:
            strength = sum(1 for other_topic in topic_names if S[topic_name][other_topic] > S[other_topic][topic_name])
            topic_strength.append((topic_name, strength))

        # Ordenar los temas por fortalezas de caminos
        sorted_topics = sorted(topic_strength, key=lambda x: x[1], reverse=True)

        # Debug: Mostrar el tema con mayor fuerza
        logger.info("Sorted topics (after Schulze algorithm):")
        logger.info(sorted_topics)

        return sorted_topics

    def calculate_positional_voting(self, topic_names, user_ids, positions_data, expertise_data):
        """
        Calculate weighted rankings using the Positional Voting algorithm.

        Parameters:
        - topic_names (list): List of topic names to evaluate.
        - user_ids (list): List of user IDs participating in the voting.
        - positions_data (dict): Dictionary mapping topic names to user positions.
        - expertise_data (dict): Dictionary mapping topic names to user expertise levels.

        Returns:
        - sorted_rankings (list): List of topics sorted by weighted rankings, in descending order.
        """
        User = apps.get_model('custom_auth', 'User')

        weighted_rankings = {}

        for topic_name in topic_names:
            total_weighted_score = 0
            total_expertise = 0

            for user_id in user_ids:
                username = User.objects.get(id=user_id).username
                pos = positions_data[topic_name].get(username, 0)
                exp = expertise_data[topic_name].get(username, 1)
                total_weighted_score += pos * exp
                total_expertise += exp

            if total_expertise > 0:
                weighted_rankings[topic_name] = total_weighted_score / total_expertise
            else:
                weighted_rankings[topic_name] = 0

        sorted_rankings = sorted(weighted_rankings.items(), key=lambda x: x[1], reverse=True)

        return sorted_rankings
