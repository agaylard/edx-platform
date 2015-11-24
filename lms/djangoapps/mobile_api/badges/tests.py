"""
Tests for the badges API views.
"""

from django.conf import settings
from mock import patch

from badges.tests.factories import BadgeAssertionFactory, BadgeClassFactory
from util.testing import UrlResetMixin
from xmodule.modulestore.tests.factories import CourseFactory
from ..testutils import MobileAPITestCase, MobileAuthUserTestMixin


class UserAssertionMixin(object):
    """
    Mixin for badge API tests.
    """
    def check_class_structure(self, badge_class, json_class):
        """
        Check a JSON response against a known badge class.
        """
        self.assertEqual(badge_class.issuing_component, json_class['issuing_component'])
        self.assertEqual(badge_class.slug, json_class['slug'])
        self.assertIn(badge_class.image.url, json_class['image'])
        self.assertEqual(badge_class.description, json_class['description'])
        self.assertEqual(badge_class.criteria, json_class['criteria'])
        self.assertEqual(badge_class.course_id and unicode(badge_class.course_id), json_class['course_id'])

    def check_assertion_structure(self, assertion, json_assertion):
        """
        Check a JSON response against a known assertion object.
        """
        self.assertEqual(assertion.image_url, json_assertion['image_url'])
        self.assertEqual(assertion.assertion_url, json_assertion['assertion_url'])
        self.assertTrue(json_assertion['user'].startswith('http'))
        self.check_class_structure(assertion.badge_class, json_assertion['badge_class'])


class TestUserBadgeAssertions(MobileAPITestCase, MobileAuthUserTestMixin, UrlResetMixin, UserAssertionMixin):
    """
    Test the general badge assertions retrieval view.
    """
    REVERSE_INFO = {'name': 'user-assertions', 'params': ['username']}

    @patch.dict(settings.FEATURES, {"ENABLE_OPENBADGES": True})
    def setUp(self):
        super(TestUserBadgeAssertions, self).setUp()

    def test_get_assertions(self):
        """
        Verify we can get all of a user's badge assertions.
        """
        self.login()
        # pylint: disable=expression-not-assigned
        [BadgeAssertionFactory.create(user=self.user) for _i in range(3)]
        # Should not be included.
        # pylint: disable=expression-not-assigned
        [BadgeAssertionFactory.create() for _i in range(3)]
        response = self.api_response(username=self.user.username, expected_response_code=200)
        self.assertEqual(len(response.data['results']), 3)

    def test_assertion_structure(self):
        self.login()
        badge_class = BadgeClassFactory.create(course_id=self.course.location.course_key)
        assertion = BadgeAssertionFactory.create(user=self.user, badge_class=badge_class)
        response = self.api_response(username=self.user.username, expected_response_code=200)
        self.check_assertion_structure(assertion, response.data['results'][0])


class TestUserCourseBadgeAssertions(MobileAPITestCase, MobileAuthUserTestMixin, UrlResetMixin, UserAssertionMixin):
    """
    Test the Badge Assertions view with the course_id filter.
    """
    REVERSE_INFO = {'name': 'user-course-assertions', 'params': ['username', 'course_id']}

    @patch.dict(settings.FEATURES, {"ENABLE_OPENBADGES": True})
    def setUp(self):
        super(TestUserCourseBadgeAssertions, self).setUp()

    def test_get_assertions(self):
        """
        Verify we can get assertions via the course_id and username.
        """
        self.login()
        course_key = self.course.location.course_key
        badge_class = BadgeClassFactory.create(course_id=course_key)
        # pylint: disable=expression-not-assigned
        [BadgeAssertionFactory.create(user=self.user, badge_class=badge_class) for _i in range(3)]
        # Should not be included.
        # pylint: disable=expression-not-assigned
        [BadgeAssertionFactory.create(user=self.user) for _i in range(5)]
        # Also should not be included
        # pylint: disable=expression-not-assigned
        [BadgeAssertionFactory.create(badge_class=badge_class) for _i in range(6)]
        response = self.api_response(username=self.user.username, course_id=course_key)
        self.assertEqual(len(response.data['results']), 3)
        unused_course = CourseFactory.create()
        response = self.api_response(username=self.user.username, course_id=unused_course.location.course_key)
        self.assertEqual(len(response.data['results']), 0)

    def test_assertion_structure(self):
        """
        Verify the badge assertion structure is not mangled in this mode.
        """
        self.login()
        course_key = self.course.location.course_key
        badge_class = BadgeClassFactory.create(course_id=course_key)
        assertion = BadgeAssertionFactory.create(badge_class=badge_class, user=self.user)
        response = self.api_response(username=self.user.username, expected_response_code=200)
        self.check_assertion_structure(assertion, response.data['results'][0])


class TestUserBadgeAssertionsByClass(MobileAPITestCase, UrlResetMixin, UserAssertionMixin):
    """
    Test the Badge Assertions view with the badge class filter.
    """
    REVERSE_INFO = {'name': 'user-class-assertions', 'params': ['username', 'issuing_component', 'slug']}

    @patch.dict(settings.FEATURES, {"ENABLE_OPENBADGES": True})
    def setUp(self):
        super(TestUserBadgeAssertionsByClass, self).setUp()

    def test_get_assertions(self):
        """
        Verify we can get assertions via the badge class and username.
        """
        self.login()
        badge_class = BadgeClassFactory.create()
        # pylint: disable=expression-not-assigned
        [BadgeAssertionFactory.create(user=self.user, badge_class=badge_class) for _i in range(3)]
        # Should not be in list.
        # pylint: disable=expression-not-assigned
        [BadgeAssertionFactory.create(badge_class=badge_class) for _i in range(5)]
        # Also should not be in list.
        # pylint: disable=expression-not-assigned
        [BadgeAssertionFactory.create() for _i in range(6)]
        response = self.api_response(
            username=self.user.username,
            reverse_args={
                'issuing_component': badge_class.issuing_component,
                'slug': badge_class.slug
            },
            expected_response_code=200,
        )
        self.assertEqual(len(response.data['results']), 3)
        unused_class = BadgeClassFactory.create(slug='unused_slug', issuing_component='unused_component')
        response = self.api_response(
            username=self.user.username,
            reverse_args={
                'issuing_component': unused_class.issuing_component,
                'slug': unused_class.slug,
            },
            expected_response_code=200,
        )
        self.assertEqual(len(response.data['results']), 0)

    def check_badge_class_assertion(self, badge_class):
        """
        Given a badge class, create an assertion for the current user and fetch it, checking the structure.
        """
        assertion = BadgeAssertionFactory.create(badge_class=badge_class, user=self.user)
        response = self.api_response(
            username=self.user.username,
            reverse_args={
                'issuing_component': badge_class.issuing_component,
                'slug': badge_class.slug,
            },
            expected_response_code=200
        )
        self.check_assertion_structure(assertion, response.data['results'][0])

    def test_assertion_structure(self):
        self.login()
        self.check_badge_class_assertion(BadgeClassFactory.create())

    def test_empty_issuing_component(self):
        self.login()
        self.check_badge_class_assertion(BadgeClassFactory.create(issuing_component=''))


class TestBadgeClass(MobileAPITestCase, UrlResetMixin, UserAssertionMixin):
    """
    Test the badge class view.
    """
    REVERSE_INFO = {'name': 'badge_class-detail', 'params': ['issuing_component', 'slug']}

    @patch.dict(settings.FEATURES, {"ENABLE_OPENBADGES": True})
    def setUp(self):
        super(TestBadgeClass, self).setUp()

    def get_badge_class(self):
        """
        Test fetching a badge class.
        """
        badge_class = BadgeClassFactory(course_id=self.course.location.course_key)
        response = self.api_response(
            reverse_args={
                'issuing_component': badge_class.issuing_component,
                'slug': badge_class.slug,
            },
            expected_response_code=200
        )
        self.assertEqual(badge_class.issuing_component, response.data['issuing_component'])
        self.assertEqual(badge_class.slug, response.data['slug'])
        self.assertEqual(badge_class.display_name, response.data['display_name'])
        self.assertEqual(badge_class.criteria, response.data['criteria'])
        self.assertEqual(badge_class.description, response.data['description'])
        self.assertEqual(unicode(badge_class.course_id), response.data['course_id'])
        # pylint: disable=no-member
        self.assertIn(badge_class.image.url, response.data['image'])
        self.check_class_structure(badge_class, response.data)
