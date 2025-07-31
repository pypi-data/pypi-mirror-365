""" Test cases for adding information to the database """

from unittest import TestCase
import pytest
from prompter.prompter import PromptGenerator,PrompterAddError,PrompterSectionAddException

class Addition(TestCase):
    """ Class for testing different add scenarios """
    def setUp(self):
        """ Initialize instance """
        self.prompt = PromptGenerator()

    def test_without_args(self):
        """ Test default behaviour without arguments """
        with pytest.raises(PrompterAddError):
            self.prompt.add()

    def test_add_duplicate(self):
        """ Test if user attempts to add duplicate """
        with pytest.raises(PrompterAddError):
            self.prompt.add("testpeople","testactivity","testlocation")
            self.prompt.add("testpeople","testactivity","testlocation")
        self.prompt.delete('testpeople')
        self.prompt.delete('testactivity')
        self.prompt.delete('testlocation')

    def test_add_to_section_nonexistent(self):
        """ Test if user tries to add to non-existent section """
        with pytest.raises(PrompterSectionAddException):
            self.prompt.add_to_section("nonexisten","nonexistentvalue")

    def test_add_to_section_duplicate_value(self):
        """ Test adding duplicate values to sections """
        with pytest.raises(PrompterSectionAddException):
            self.prompt.add_to_section("people","Julius Caesar")
