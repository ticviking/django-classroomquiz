from django import forms

from hackinged.quizengine.models import Answer

class NewQuizForm(forms.Form):
    name = forms.CharField(required = True)
    
class NewQuestionForm(forms.Form):#TODO make this a factory
    question = forms.CharField(required = True)
    value = forms.IntegerField(label = "Value")
    answer_a = forms.CharField(label = "A.")
    a_is_correct = forms.BooleanField(label = "Is A. the correct answer?", required = False)
    answer_b = forms.CharField(label = "B.")
    b_is_correct = forms.BooleanField(label = "Is B. the correct answer?", required = False)
    answer_c = forms.CharField(label = "C.")
    c_is_correct = forms.BooleanField(label = "Is C. the correct answer?", required = False)
    answer_d = forms.CharField(label = "D.")
    d_is_correct = forms.BooleanField(label = "Is D. the correct answer?", required = False)
    

def take_quiz_factory(quiz):
    """takes a quiz object and returns a form of
    all questions associated with the quiz."""
    fields = {}
    questions = quiz.question_set.all()
    for question in questions:
        field_name = "question_%d" %question.pk
        choices = []
        for answer in question.answer_set.all():
            choices.append((answer.pk, answer.answer,))
        fields[field_name] = forms.ChoiceField(label=question.question,
                                               required=True,
                                               choices=choices,
                                               widget=forms.RadioSelect)
    return type('TakeQuizForm', (forms.BaseForm,), {'base_fields': fields})
