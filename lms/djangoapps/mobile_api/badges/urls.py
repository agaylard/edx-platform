"""
URLs for badges API
"""
from django.conf.urls import patterns, url
from django.conf import settings

from mobile_api.badges.views import BadgeClassDetail, UserBadgeAssertions
from openedx.core.djangoapps.user_api.urls import USERNAME_PATTERN

BADGE_PATTERN = r'(?P<issuing_component>[-\w]*)/(?P<slug>[-\w]+)'

urlpatterns = patterns(
    'mobile_api.badges.views',
    url('^classes/' + BADGE_PATTERN + '/$', BadgeClassDetail.as_view(), name='badge_class-detail'),
    url('^assertions/user/' + USERNAME_PATTERN + '/$', UserBadgeAssertions.as_view(), name='user-assertions'),
    url(
        '^assertions/user/' + USERNAME_PATTERN + '/' + settings.COURSE_ID_PATTERN + '/$', UserBadgeAssertions.as_view(),
        name='user-course-assertions',
    ),
    url(
        '^assertions/class/' + BADGE_PATTERN + '/' + 'user' + '/' + USERNAME_PATTERN + '/$',
        UserBadgeAssertions.as_view(), name='user-class-assertions'
    )
)
