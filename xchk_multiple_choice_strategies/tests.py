import unittest
from unittest.mock import MagicMock, patch
from django.test import TestCase
from xchk_multiple_choice_strategies.strats import MultipleChoiceFormatCheck, MultipleChoiceAnswerCheck
from xchk_core.strats import OutcomeAnalysis, OutcomeComponent
from xchk_core.models import Submission

class MultipleChoiceFormatCheckTest(TestCase):

    def test_valid_input(self):
        # will need to patch open, just providing won't work here because of how antlr reads filestream
        chk = MultipleChoiceFormatCheck(filename='myfile.txt')
        submission = Submission()
        with patch('builtins.open') as mock_open:
            # https://github.com/antlr/antlr4/blob/master/runtime/Python3/src/antlr4/FileStream.py
            # need to mock read() method
            mock_open.return_value.__enter__.return_value.read.return_value = b'1 A 2 B C 3 D'
            outcome = chk.check_submission(submission=submission,student_path='/student',desired_outcome=True,init_check_number=1,ancestor_has_alternatives=False,parent_is_negation=False)
            expected = OutcomeAnalysis(outcome=True,outcomes_components=[OutcomeComponent(component_number=1,outcome=True,desired_outcome=True,rendered_data=None,acceptable_to_ancestor=True)])
            self.assertEqual(outcome,expected)

    def test_invalid_input_starting_with_letters(self):
        chk = MultipleChoiceFormatCheck(filename='myfile.txt')
        submission = Submission()
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b'AAAA1 A 2 B C 3 D'
            outcome = chk.check_submission(submission=submission,student_path='/student',desired_outcome=True,init_check_number=1,ancestor_has_alternatives=False,parent_is_negation=False)
            expected = OutcomeAnalysis(outcome=False,outcomes_components=[OutcomeComponent(component_number=1,outcome=False,desired_outcome=True,rendered_data='<p>Het formaat voor meerkeuzevragen is als volgt:</p>',acceptable_to_ancestor=False)])
            self.assertEqual(outcome,expected)

    def test_invalid_input_containing_dollar_symbol(self):
        chk = MultipleChoiceFormatCheck(filename='myfile.txt')
        submission = Submission()
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
        submission = Submission()
        with patch('builtins.open') as mock_open:
            # https://github.com/antlr/antlr4/blob/master/runtime/Python3/src/antlr4/FileStream.py
            # need to mock read() method
            mock_open.return_value.__enter__.return_value.read.return_value = b'1 B 2 B 3 A'
            outcome = chk.check_submission(submission=submission,student_path='/student',desired_outcome=True,init_check_number=1,ancestor_has_alternatives=False,parent_is_negation=False)
            expected = OutcomeAnalysis(outcome=True,outcomes_components=[OutcomeComponent(component_number=1,outcome=True,desired_outcome=True,rendered_data=None,acceptable_to_ancestor=True)])
            self.assertEqual(outcome,expected)

    def test_invalid_answers(self):
        # will need to patch open, just providing won't work here because of how antlr reads filestream
        mc_data = [("Rozen zijn (meestal)",
                    ("Rood",True,"Mis je geen kleur die op de naam van de bloem lijkt?"),
                    ("Bloemen",True,"Je weet toch wat rozen zijn?"),
                    ("Groen",False,"Komaan, je weet dat het over de blaadjes gaat.")),
                   ("Weten studenten altijd hoe ze studiemateriaal moeten benaderen?",
                    ("Ja",False,"Als dat waar is, waarom vragen we hen dan niet gewoon alles zelf op te zoeken?"),
                    ("Nee",True,"Als dat niet onwaar is, waarom vragen we hen dan niet gewoon alles zelf op te zoeken?"))] 
        chk = MultipleChoiceAnswerCheck(filename='myfile.txt',mc_data=mc_data)
        submission = Submission()
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b'1 C 2 A'
            outcome = chk.check_submission(submission=submission,student_path='/student',desired_outcome=True,init_check_number=1,ancestor_has_alternatives=False,parent_is_negation=False)
            print(outcome)
            expected = OutcomeAnalysis(outcome=False,outcomes_components=[OutcomeComponent(component_number=1,outcome=False,desired_outcome=True,rendered_data='<p>Je mist correcte antwoorden of je hebt verkeerde antwoorden. Gebruik onderstaande hints om je inzending te corrigeren. Je krijgt een paar hints per inzending. Gebruik deze om de stof beter te begrijpen en pas dan je antwoord aan. Het heeft geen zin alle combinaties te proberen, want dan saboteer je je eigen begrip van de leerstof.</p><ul><li>Vraag 1: Je weet toch wat rozen zijn?</li><li>Vraag 1: Komaan, je weet dat het over de blaadjes gaat.</li><li>Vraag 1: Mis je geen kleur die op de naam van de bloem lijkt?</li></ul>',acceptable_to_ancestor=False)])
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
