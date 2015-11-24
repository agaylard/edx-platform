"""
Mobile API views for badges
"""
from edxval.views import MultipleFieldLookupMixin
from opaque_keys.edx.keys import CourseKey
from rest_framework import generics

from badges.models import BadgeClass, BadgeAssertion
from mobile_api.badges.serializers import BadgeClassSerializer, BadgeAssertionSerializer
from mobile_api.utils import mobile_view


@mobile_view()
class BadgeClassDetail(MultipleFieldLookupMixin, generics.RetrieveAPIView):
    """
    Get the details of a specific badge class.
    """
    queryset = BadgeClass.objects.all()
    serializer_class = BadgeClassSerializer
    lookup_fields = ('issuing_component', 'slug')


@mobile_view(is_user=True)
class UserBadgeAssertions(generics.ListAPIView):
    """
    Get all badge assertions for a user, optionally constrained to a course.
    """
    serializer_class = BadgeAssertionSerializer

    def get_queryset(self):
        """
        Get all badges for the username specified.
        """
        queryset = BadgeAssertion.objects.filter(user__username=self.kwargs['username'])
        if self.kwargs.get('course_id'):
            queryset = queryset.filter(badge_class__course_id=CourseKey.from_string(self.kwargs['course_id']))
        if self.kwargs.get('slug'):
            queryset = queryset.filter(
                badge_class__slug=self.kwargs['slug'],
                badge_class__issuing_component=self.kwargs.get('issuing_component', '')
            )
        return queryset
