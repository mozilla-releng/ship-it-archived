import unittest

from datetime import datetime, timedelta, tzinfo

from kickoff.utils import parse_iso8601_to_date_time


class TestRelease(unittest.TestCase):
    def testParseIso8601ToDateTime(self):
        test_values = ({
            'value': '2017-01-02T03:04:05+00:00',
            'expected': datetime(year=2017, month=1, day=2, hour=3, minute=4, second=5),
        }, {
            'value': '2017-01-02T03:04:05-06:00',
            'expected': datetime(year=2017, month=1, day=2, hour=9, minute=4, second=5),
        }, {
            'value': '2017-01-02T03:04:05+06:00',
            'expected': datetime(year=2017, month=1, day=1, hour=21, minute=4, second=5),
        })

        for test_value in test_values:
            self.assertEqual(parse_iso8601_to_date_time(test_value['value']), test_value['expected'])

    def testValidButUnexpectedIso8601(self):
        test_values = ({
            'value': '2017-01-02T03:04:05.000',
            'expected': ValueError,
        }, {
            'value': '2017-01-02T03:04+00:00',
            'expected': ValueError,
        }, {
            'value': '2017-01-02T03:04:05.00+00:00',
            'expected': ValueError,
        })

        for test_value in test_values:
            self.assertRaises(test_value['expected'], parse_iso8601_to_date_time, test_value['value'])
