# -*- coding: utf-8 -*-
"""
Tests for tracking logger.
"""
from __future__ import absolute_import

import json
import logging
import datetime
from mock import patch

from django.test import TestCase

from track.backends.logger import LoggerBackend


class TestLoggerBackend(TestCase):
    def setUp(self):
        super(TestLoggerBackend, self).setUp()
        self.handler = MockLoggingHandler()
        self.handler.setLevel(logging.INFO)

        logger_name = 'track.backends.logger.test'
        logger = logging.getLogger(logger_name)
        logger.addHandler(self.handler)

        self.backend = LoggerBackend(name=logger_name)
        self.handler.reset()

    def test_logger_backend(self):
        # Send a couple of events and check if they were recorded
        # by the logger. The events are serialized to JSON.

        event = {
            'test': True,
            'time': datetime.datetime(2012, 05, 01, 07, 27, 01, 200),
            'date': datetime.date(2012, 05, 07),
        }

        self.backend.send(event)
        self.backend.send(event)

        saved_events = [json.loads(e) for e in self.handler.messages['info']]

        unpacked_event = {
            'test': True,
            'time': '2012-05-01T07:27:01.000200+00:00',
            'date': '2012-05-07'
        }

        self.assertEqual(saved_events[0], unpacked_event)
        self.assertEqual(saved_events[1], unpacked_event)

    @patch('track.backends.logger.application_log')
    def test_logger_backend_unicode_character(self, application_log):
        """
        When event information contain utf and latin1 characters
        """
        # Utf-8 characters
        unicode_characters = {
            'unicode': u'测试',
            'string': '测试',
            'encoded_unicode': u'测试'.encode('utf-8')
        }
        # Latin1 characters
        latin_characters = {
            'unicode_latin': u'Ó é ñ',
            'string_latin': 'Ó é ñ',
            'encoded_latin': u'Ó é ñ'.encode('latin1'),
            'level_1': {'encoded_latin': u'Ó é ñ'.encode('latin1')}
        }

        self.backend.send(unicode_characters)
        self.backend.send(latin_characters)
        # latin_characters dict will raise UnicodeDecodeError due to encoded_latin and also
        # ensure that only called with effected event item data.
        application_log.exception.assert_called_with(
            "UnicodeDecodeError Event-Data: %s", latin_characters
        )
        self.assertEqual(application_log.exception.call_count, 1)

        saved_events = [json.loads(e) for e in self.handler.messages['info']]
        self.assertEqual(saved_events[0]['unicode'], unicode_characters['unicode'])
        self.assertEqual(saved_events[0]['string'], unicode_characters['unicode'])
        self.assertEqual(saved_events[0]['encoded_unicode'], unicode_characters['unicode'])
        self.assertEqual(saved_events[1]['unicode_latin'], latin_characters['unicode_latin'])
        self.assertEqual(saved_events[1]['string_latin'], latin_characters['unicode_latin'])
        self.assertEqual(saved_events[1]['encoded_latin'], latin_characters['unicode_latin'])
        self.assertEqual(saved_events[1]['level_1']['encoded_latin'], latin_characters['unicode_latin'])


class MockLoggingHandler(logging.Handler):
    """
    Mock logging handler.

    Stores records in a dictionry of lists by level.

    """

    def __init__(self, *args, **kwargs):
        super(MockLoggingHandler, self).__init__(*args, **kwargs)
        self.messages = None
        self.reset()

    def emit(self, record):
        level = record.levelname.lower()
        message = record.getMessage()
        self.messages[level].append(message)

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }
