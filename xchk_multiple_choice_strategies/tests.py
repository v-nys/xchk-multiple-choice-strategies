import unittest
from unittest.mock import MagicMock, patch
from django.test import TestCase
from xchk_multiple_choice_strategies.strats import MultipleChoiceFormatCheck, MultipleChoiceAnswerCheck
from xchk_core.strats import OutcomeAnalysis, OutcomeComponent
from xchk_core.models import SubmissionV2

class MultipleChoiceFormatCheckTest(TestCase):

    def test_valid_input(self):
        # will need to patch open, just providing won't work here because of how antlr reads filestream
        chk = MultipleChoiceFormatCheck(filename='myfile.txt')
        submission = SubmissionV2()
        with patch('builtins.open') as mock_open:
            # https://github.com/antlr/antlr4/blob/master/runtime/Python3/src/antlr4/FileStream.py
            # need to mock read() method
            mock_open.return_value.__enter__.return_value.read.return_value = b'1 A 2 B C 3 D'
            outcome = chk.check_submission(submission=submission,student_path='/student',desired_outcome=True,init_check_number=1,ancestor_has_alternatives=False,parent_is_negation=False)
            expected = OutcomeAnalysis(outcome=True,outcomes_components=[OutcomeComponent(component_number=1,outcome=True,desired_outcome=True,rendered_data=None,acceptable_to_ancestor=True)])
            self.assertEqual(outcome,expected)

    def test_invalid_input_starting_with_letters(self):
        chk = MultipleChoiceFormatCheck(filename='myfile.txt')
        submission = SubmissionV2()
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b'AAAA1 A 2 B C 3 D'
            outcome = chk.check_submission(submission=submission,student_path='/student',desired_outcome=True,init_check_number=1,ancestor_has_alternatives=False,parent_is_negation=False)
            expected = OutcomeAnalysis(outcome=False,outcomes_components=[OutcomeComponent(component_number=1,outcome=False,desired_outcome=True,rendered_data='<p>Het formaat voor meerkeuzevragen is als volgt:</p>',acceptable_to_ancestor=False)])
            self.assertEqual(outcome,expected)

    def test_invalid_input_containing_dollar_symbol(self):
        chk = MultipleChoiceFormatCheck(filename='myfile.txt')
        submission = SubmissionV2()
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b'//blabla\n1\n$\n//blabla\nA\nB'
            outcome = chk.check_submission(submission=submission,student_path='/student',desired_outcome=True,init_check_number=1,ancestor_has_alternatives=False,parent_is_negation=False)
            expected = OutcomeAnalysis(outcome=False,outcomes_components=[OutcomeComponent(component_number=1,outcome=False,desired_outcome=True,rendered_data='<p>Het formaat voor meerkeuzevragen is als volgt:</p>',acceptable_to_ancestor=False)])
            self.assertEqual(outcome,expected)

class MultipleChoiceAnswerCheckTest(TestCase):

    def test_valid_answers(self):
        # will need to patch open, just providing won't work here because of how antlr reads filestream
        mc_data = [("Is kennis lineair gestructureerd?",
                    ("Ja",False,"Leert iedereen altijd alles in dezelfde volgorde?"),
                    ("Nee",True,None)),
                   ("Weten studenten altijd hoe ze studiemateriaal moeten benaderen?",
                    ("Ja",False,"Waarom vragen we hen dan niet gewoon alles zelf op te zoeken?"),
                    ("Nee",True,None)),
                   ("Maken lectoren soms assumpties over voorkennis?",
                    ("Ja",True,"Het is je nog nooit overkomen dat er iets gevraagd werd dat je niet in de les hebt gezien?"),
                    ("Nee",False,None))] 
        chk = MultipleChoiceAnswerCheck(filename='myfile.txt',mc_data=mc_data)
        submission = SubmissionV2()
        with patch('builtins.open') as mock_open:
            # https://github.com/antlr/antlr4/blob/master/runtime/Python3/src/antlr4/FileStream.py
            # need to mock read() method
            mock_open.return_value.__enter__.return_value.read.return_value = b'1 B 2 B 3 A'
            outcome = chk.check_submission(submission=submission,student_path='/student',desired_outcome=True,init_check_number=1,ancestor_has_alternatives=False,parent_is_negation=False)
            expected = OutcomeAnalysis(outcome=True,outcomes_components=[OutcomeComponent(component_number=1,outcome=True,desired_outcome=True,rendered_data=None,acceptable_to_ancestor=True)])
            self.assertEqual(outcome,expected)

class MultipleChoiceRenderedListTest(TestCase):

    def test_realistic_list(self):
        mc_data = [("A?",
                    ("B",False,None),
                    ("C",True,None)),
                   ("D?",
                    ("E",False,None),
                    ("F",True,None))] 
        chk = MultipleChoiceAnswerCheck(filename=None,mc_data=mc_data)
        outcome = chk.render()
        expected = '<ol class="multiple-choice"><li>A?<ol><li>B</li><li>C</li></ol></li><li>D?<ol><li>E</li><li>F</li></ol></li></ol>'
        self.assertIn(expected,outcome)

if __name__ == '__main__':
    unittest.main()
