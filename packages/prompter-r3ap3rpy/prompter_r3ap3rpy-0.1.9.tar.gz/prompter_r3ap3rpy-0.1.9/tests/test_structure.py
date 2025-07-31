""" Test for the structure of the internal database """

from unittest import TestCase
from prompter.prompter import PromptGenerator

class Structure(TestCase):
    """ Testcase definitions """
    def setUp(self):
        """ Initialize the instance """
        self.prompt = PromptGenerator()

    def test_stats_keys(self):
        """ Test if we have sections """
        assert len(self.prompt.raw_data.keys()) > 0

    def test_stats_keys_length(self):
        """ Test if they have length """
        for key in self.prompt.raw_data:
            assert len(self.prompt.raw_data[key]) > 0
