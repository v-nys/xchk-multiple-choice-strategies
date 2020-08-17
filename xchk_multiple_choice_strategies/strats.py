import os
from antlr4 import *
from xchk_core.strats import CheckingPredicate, Strategy, OutcomeComponent, OutcomeAnalysis, StratInstructions

from .MultipleChoiceLexer import MultipleChoiceLexer
from .MultipleChoiceParser import MultipleChoiceParser
from .MultipleChoiceChecker import MultipleChoiceChecker

class MultipleChoiceAnswerCheck(CheckingPredicate):

    def __init__(self,filename,mc_data):
        self.filename = filename
        self.mc_data = mc_data

    def _entry(self,exercise_name):
        return self.filename or exercise_name

    def component_checks(self):
        return []

    def instructions(self,exercise_name,init_check_number):
        return [f'Je hebt alle correcte antwoorden per vraag aangeduid.']

    def negative_instructions(self,exercise_name,init_check_number):
        return [f'Je hebt niet alle correcte antwoorden per vraag aangeduid.']

    def render(self):
        def _answers_as_lis(q_tuple):
            return ''.join([f'<li>{a[0]}</li>' for a in q[1:-1]])
        questions_as_lis = ''.join([f"<li>{q[0]}<ul>{_answers_as_lis(q)}</ul></li>" for q in self.mc_data])
        return f'<ul class=multiple-choice>{questions_as_lis}</ul>'

    def check_submission(self,submission,student_path,desired_outcome,init_check_number,ancestor_has_alternatives,parent_is_negation=False,open=open):
        # moet bij elke vraag nummer controleren (moet volgen op vorig, dat begint bij 0)
        # moet bij elke vraag controleren of de antwoorden (na lower case) voorkomen in de reeks antwoorden
        # hier moeten we ja/nee zeggen en de relatie tot gewenste uitkomst geven
        # is niet duidelijk bij gelijk welke exception, dus beter niveau hoger afhandelen?
        input_stream = FileStream(os.path.join(student_path,self._entry(submission.content_uid)))
        lexer = MultipleChoiceLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = MultipleChoiceParser(stream)
        tree = parser.multiplechoice()
        checker = MultipleChoiceChecker(self.mc_data)
        walker = ParseTreeWalker()
        walker.walk(checker,tree)
        overall_outcome = len(checker.error_list) == 0
        components = [OutcomeComponent(component_number=init_check_number,
                                       outcome=overall_outcome,
                                       desired_outcome=desired_outcome,
                                       rendered_data="meer doen met errorlist" if overall_outcome != desired_outcome else None,
                                       acceptable_to_ancestor = overall_outcome == desired_outcome or ancestor_has_alternatives)]
        return OutcomeAnalysis(outcome=overall_outcome,
                               outcomes_components=components)

class MultipleChoiceFormatCheck(CheckingPredicate):

    def __init__(self,filename=None):
        self.filename = filename

    def _entry(self,exercise_name):
        return self.filename or exercise_name

    def instructions(self,exercise_name):
        """Returns a hierarchical representation of the explicit conditions to be met for this check to return `True`."""
        return [f"Je inzending volgt het vaste formaat voor meerkeuzevragen."]

    def negative_instructions(self,exercise_name):
        """Returns a hierarchical representation of the explicit conditions to be met for this check to return `False`."""
        return [f"Je inzending volgt niet het vaste formaat voor meerkeuzevragen."]

    def component_checks(self):
        return []

    def check_submission(self,submission,student_path,desired_outcome,init_check_number,ancestor_has_alternatives,parent_is_negation=False,open=open):
        # with open(os.path.join(student_path,self._entry(submission.content_uid))) as fhs:
        input_stream = FileStream(os.path.join(student_path,self._entry(submission.content_uid)))
        lexer = MultipleChoiceLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = MultipleChoiceParser(token_stream)
        tree = parser.multiplechoice()
        overall_outcome = parser.getNumberOfSyntaxErrors() == 0
        components = [OutcomeComponent(component_number=init_check_number,
                                       outcome=overall_outcome,
                                       desired_outcome=desired_outcome,
                                       rendered_data="<p>Het formaat voor meerkeuzevragen is als volgt:</p>" if overall_outcome != desired_outcome else None,
                                       acceptable_to_ancestor = overall_outcome == desired_outcome or ancestor_has_alternatives)]
        return OutcomeAnalysis(outcome=overall_outcome,
                               outcomes_components=components)

# if desired, define strategies by subclassing Strategy
# override __init__ so that refusing_check and accepting_check are hardwired
