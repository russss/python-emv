from __future__ import division, absolute_import, print_function, unicode_literals

# coding=utf-8
from unittest2 import TestCase
from emv.protocol.data_elements import ELEMENT_TABLE


class TestDataElements(TestCase):
    def test_data_elements(self):
        # Test uniqueness of the main element table
        seen_tags = set()
        seen_shortnames = set()
        for tag, name, parse, shortname in ELEMENT_TABLE:
            self.assertNotIn(tag, seen_tags)
            if shortname is not None:
                self.assertNotIn(shortname, seen_shortnames)
                seen_shortnames.add(shortname)
            seen_tags.add(tag)
