"""Utility functions and classes for track backends"""

from datetime import datetime, date
import json

from pytz import UTC


class DateTimeJSONEncoder(json.JSONEncoder):
    """JSON encoder aware of datetime.datetime and datetime.date objects"""

    def default(self, obj):  # pylint: disable=method-hidden
        """
        Serialize datetime and date objects of iso format.

        datatime objects are converted to UTC.
        """
        if isinstance(obj, datetime):
            if obj.tzinfo is None:
                # Localize to UTC native datetime objects
                obj = UTC.localize(obj)
            else:
                # Convert to UTC datetime objects from other timezones
                obj = obj.astimezone(UTC)
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()

        return super(DateTimeJSONEncoder, self).default(obj)


class LatinJSONEncoder(DateTimeJSONEncoder):
    """
    JSON encoder for UnicodeDecodeError with latin1 characters
    """

    def encode(self, obj):
        """
        Returns json-encoded representation `of obj.
        """
        obj = self.iterate_dictionary(obj)

        return super(LatinJSONEncoder, self).encode(obj)

    def iterate_dictionary(self, obj):
        """
        This tests that all strings are decodeable as utf8. If some string is not, it then tries instead to decode as
        latin1, and if succeeds, tries to "fix" by substituting the decoded string.
        """
        for key, value in obj.iteritems():
            if isinstance(value, dict):
                self.iterate_dictionary(value)
            elif isinstance(value, str):
                try:
                    # Will throw UnicodeDecodeError in cases when there are
                    # latin1 encoded characters in string.
                    #  Example {'string': '\xd3 \xe9 \xf1'}
                    obj[key].decode('utf8')
                except UnicodeDecodeError:
                    obj[key] = obj[key].decode('latin1')
        return obj
