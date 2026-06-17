import pytest
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.custom_auth.domain.entities.group import Group, GroupUser
from apps.concensus.domain.entities.debate import Debate
from apps.concensus.domain.entities.debate_message import Message
from apps.concensus.domain.entities.debate_participant import DebateParticipant
from apps.concensus.domain.entities.topic import Topic, RecommendedTopic, TopicAddedUser

User = get_user_model()


class TopicModelTest(TestCase):
    """Tests for Topic creation and association with a group."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin@centinela.epn.ec",
            password="AdminPass123!",
            first_name="Admin",
            last_name="User"
        )
        self.group = Group.objects.create(
            title="Research Group",
            description="A group for research discussion",
            admin=self.admin_user
        )

    def test_topic_creation(self):
        topic = Topic.objects.create(name="Artificial Intelligence", group=self.group)
        self.assertEqual(topic.name, "Artificial Intelligence")
        self.assertEqual(topic.group, self.group)

    def test_topic_str_representation(self):
        topic = Topic.objects.create(name="Machine Learning", group=self.group)
        self.assertEqual(str(topic), "Machine Learning")

    def test_topic_belongs_to_group(self):
        topic = Topic.objects.create(name="Deep Learning", group=self.group)
        self.assertEqual(topic.group.id, self.group.id)
        self.assertEqual(topic.group.title, "Research Group")

    def test_multiple_topics_per_group(self):
        Topic.objects.create(name="Topic 1", group=self.group)
        Topic.objects.create(name="Topic 2", group=self.group)
        Topic.objects.create(name="Topic 3", group=self.group)
        self.assertEqual(Topic.objects.filter(group=self.group).count(), 3)

    def test_recommended_topic_creation(self):
        rec_topic = RecommendedTopic.objects.create(
            topic_name="Quantum Computing",
            group=self.group
        )
        self.assertEqual(rec_topic.topic_name, "Quantum Computing")
        self.assertEqual(rec_topic.group, self.group)
        self.assertEqual(str(rec_topic), "Quantum Computing")

    def test_recommended_topic_group_nullable(self):
        rec_topic = RecommendedTopic.objects.create(
            topic_name="Orphan Topic",
            group=None
        )
        self.assertIsNone(rec_topic.group)

    def test_topic_added_user(self):
        rec_topic = RecommendedTopic.objects.create(
            topic_name="Blockchain",
            group=self.group
        )
        added = TopicAddedUser.objects.create(
            topic=rec_topic,
            group=self.group,
            user=self.admin_user
        )
        self.assertEqual(added.topic, rec_topic)
        self.assertEqual(added.group, self.group)
        self.assertEqual(added.user, self.admin_user)
        self.assertIsNotNone(added.added_at)


class DebateModelTest(TestCase):
    """Tests for Debate creation and behavior."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="debate_admin@centinela.epn.ec",
            password="DebatePass123!",
            first_name="Debate",
            last_name="Admin"
        )
        self.group = Group.objects.create(
            title="Debate Group",
            description="Group for debates",
            admin=self.admin_user
        )

    def test_debate_creation(self):
        debate = Debate.objects.create(
            group=self.group,
            title="Should AI be regulated?",
            description="Discussion about AI regulation.",
            end_time=timedelta(hours=2)
        )
        self.assertEqual(debate.title, "Should AI be regulated?")
        self.assertEqual(debate.description, "Discussion about AI regulation.")
        self.assertEqual(debate.group, self.group)

    def test_debate_is_closed_default_false(self):
        debate = Debate.objects.create(
            group=self.group,
            title="Open Debate",
            description="A new debate that should be open.",
            end_time=timedelta(hours=1)
        )
        self.assertFalse(debate.is_closed)

    def test_debate_can_be_closed(self):
        debate = Debate.objects.create(
            group=self.group,
            title="Closeable Debate",
            description="This debate will be closed.",
            end_time=timedelta(hours=1),
            is_closed=True
        )
        self.assertTrue(debate.is_closed)

    def test_debate_str_representation(self):
        debate = Debate.objects.create(
            group=self.group,
            title="Ethics in AI",
            description="Debate on ethical AI.",
            end_time=timedelta(minutes=30)
        )
        self.assertEqual(str(debate), "Ethics in AI - Debate Group")

    def test_debate_end_time_duration(self):
        duration = timedelta(hours=3, minutes=30)
        debate = Debate.objects.create(
            group=self.group,
            title="Long Debate",
            description="A long discussion.",
            end_time=duration
        )
        self.assertEqual(debate.end_time, duration)

    def test_debate_get_closing_time(self):
        duration = timedelta(hours=2)
        debate = Debate.objects.create(
            group=self.group,
            title="Timed Debate",
            description="Testing closing time.",
            end_time=duration
        )
        # created_at is auto-populated; closing time = created_at + end_time
        debate.refresh_from_db()
        expected_closing = debate.created_at + duration
        self.assertEqual(debate.get_closing_time(), expected_closing)

    def test_debate_belongs_to_group(self):
        debate = Debate.objects.create(
            group=self.group,
            title="Group Debate",
            description="Belongs to a group.",
            end_time=timedelta(hours=1)
        )
        self.assertEqual(debate.group.title, "Debate Group")


class MessageModelTest(TestCase):
    """Tests for Message (DebateMessage) and posture choices validation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="msg_user@centinela.epn.ec",
            password="MsgPass123!",
            first_name="Message",
            last_name="User"
        )
        self.group = Group.objects.create(
            title="Message Group",
            description="Group for message testing",
            admin=self.user
        )
        self.debate = Debate.objects.create(
            group=self.group,
            title="Message Debate",
            description="A debate with messages.",
            end_time=timedelta(hours=1)
        )

    def test_message_creation_with_default_posture(self):
        message = Message.objects.create(
            user=self.user,
            debate=self.debate,
            text="I think this is a good point."
        )
        self.assertEqual(message.posture, 'neutral')
        self.assertEqual(message.text, "I think this is a good point.")

    def test_message_posture_agree(self):
        message = Message.objects.create(
            user=self.user,
            debate=self.debate,
            text="I agree with this proposal.",
            posture='agree'
        )
        self.assertEqual(message.posture, 'agree')

    def test_message_posture_disagree(self):
        message = Message.objects.create(
            user=self.user,
            debate=self.debate,
            text="I disagree with this approach.",
            posture='disagree'
        )
        self.assertEqual(message.posture, 'disagree')

    def test_message_posture_neutral(self):
        message = Message.objects.create(
            user=self.user,
            debate=self.debate,
            text="I have no strong opinion.",
            posture='neutral'
        )
        self.assertEqual(message.posture, 'neutral')

    def test_message_invalid_posture_raises_validation_error(self):
        message = Message(
            user=self.user,
            debate=self.debate,
            text="Invalid posture test.",
            posture='invalid_choice'
        )
        with self.assertRaises(ValidationError):
            message.full_clean()

    def test_message_str_representation(self):
        message = Message.objects.create(
            user=self.user,
            debate=self.debate,
            text="Test message."
        )
        expected = f"Message by {self.user.username} in {self.debate.title}"
        self.assertEqual(str(message), expected)

    def test_message_with_group(self):
        message = Message.objects.create(
            user=self.user,
            group=self.group,
            debate=self.debate,
            text="Message with group context."
        )
        self.assertEqual(message.group, self.group)

    def test_message_parent_reply(self):
        parent_msg = Message.objects.create(
            user=self.user,
            debate=self.debate,
            text="Parent message."
        )
        reply_msg = Message.objects.create(
            user=self.user,
            debate=self.debate,
            text="Reply to parent.",
            parent=parent_msg
        )
        self.assertEqual(reply_msg.parent, parent_msg)
        self.assertIn(reply_msg, parent_msg.replies.all())

    def test_message_has_created_at(self):
        message = Message.objects.create(
            user=self.user,
            debate=self.debate,
            text="Timestamp test."
        )
        self.assertIsNotNone(message.created_at)


class DebateParticipantModelTest(TestCase):
    """Tests for DebateParticipant linking."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="part_admin@centinela.epn.ec",
            password="PartPass123!",
            first_name="Part",
            last_name="Admin"
        )
        self.participant_user = User.objects.create_user(
            username="participant@centinela.epn.ec",
            password="PartUser123!",
            first_name="Part",
            last_name="User"
        )
        self.group = Group.objects.create(
            title="Participant Group",
            description="Group for participant tests",
            admin=self.admin
        )
        self.debate = Debate.objects.create(
            group=self.group,
            title="Participant Debate",
            description="Debate for participant testing.",
            end_time=timedelta(hours=1)
        )

    def test_debate_participant_creation(self):
        dp = DebateParticipant.objects.create(
            debate=self.debate,
            participant=self.participant_user
        )
        self.assertEqual(dp.debate, self.debate)
        self.assertEqual(dp.participant, self.participant_user)

    def test_debate_participant_is_collaborator_default_false(self):
        dp = DebateParticipant.objects.create(
            debate=self.debate,
            participant=self.participant_user
        )
        self.assertFalse(dp.is_collaborator)

    def test_debate_participant_as_collaborator(self):
        dp = DebateParticipant.objects.create(
            debate=self.debate,
            participant=self.participant_user,
            is_collaborator=True
        )
        self.assertTrue(dp.is_collaborator)

    def test_debate_participant_str_representation(self):
        dp = DebateParticipant.objects.create(
            debate=self.debate,
            participant=self.participant_user
        )
        expected = f"{self.participant_user.username} in debate {self.debate.title}"
        self.assertEqual(str(dp), expected)

    def test_debate_participant_joined_at(self):
        dp = DebateParticipant.objects.create(
            debate=self.debate,
            participant=self.participant_user
        )
        self.assertIsNotNone(dp.joined_at)

    def test_multiple_participants_in_debate(self):
        DebateParticipant.objects.create(
            debate=self.debate,
            participant=self.admin
        )
        DebateParticipant.objects.create(
            debate=self.debate,
            participant=self.participant_user
        )
        self.assertEqual(
            DebateParticipant.objects.filter(debate=self.debate).count(), 2
        )

    def test_participant_linked_to_debate_via_related_name(self):
        DebateParticipant.objects.create(
            debate=self.debate,
            participant=self.participant_user
        )
        self.assertEqual(self.debate.participants.count(), 1)
        self.assertEqual(
            self.debate.participants.first().participant, self.participant_user
        )
