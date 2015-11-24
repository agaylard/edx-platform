"""
Serializers for Badges
"""
from rest_framework import serializers

from badges.models import BadgeClass, BadgeAssertion


class BadgeClassSerializer(serializers.ModelSerializer):
    """
    Serializer for BadgeClass model.
    """
    class Meta(object):
        model = BadgeClass
        fields = ('slug', 'issuing_component', 'display_name', 'course_id', 'description', 'criteria', 'image')


class BadgeAssertionSerializer(serializers.ModelSerializer):
    """
    Serializer for the BadgeAssertion model.
    """
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', lookup_field='username', read_only=True)
    badge_class = BadgeClassSerializer(read_only=True)

    class Meta(object):
        model = BadgeAssertion
        fields = ('user', 'badge_class', 'image_url', 'assertion_url')
