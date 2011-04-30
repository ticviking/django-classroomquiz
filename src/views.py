from __future__ import division

from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Count, Sum
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from hackinged.quizengine import models
from hackinged.quizengine import forms


def index(request):
    c = RequestContext(request)
    if request.user.is_authenticated():
        latest_quizzes = models.Quiz.objects.exclude(
            creator = request.user).order_by('-creation')[:5]
        my_quizzes = models.Quiz.objects.filter(
            creator = request.user).order_by('-creation')[:5]
        return render_to_response('quizengine/list_quizzes.html',
                                 {'latest_quizzes': latest_quizzes,
                                  'page_name': 'Quizengine 0.01',
                                  'my_quizzes': my_quizzes},
                                  context_instance = c)
    latest_quizzes = models.Quiz.objects.all().order_by('-creation')[:5]
    return render_to_response('quizengine/list_quizzes.html',
                              {'latest_quizzes': latest_quizzes},
                              context_instance = c)

@login_required
def add_quiz(request):
    if request.method == 'POST':
        form = forms.NewQuizForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_quiz = models.Quiz(name = cd['name'],
                                   creator = request.user
                                   )
            new_quiz.save()
            return HttpResponseRedirect('/quiz/%d/add' %new_quiz.id)
    else: #display a form to create a new quiz
        form = forms.NewQuizForm()
    c = RequestContext(request)
    return render_to_response('quizengine/add_quiz.html',
                              {'form' : form,
                               'page_name' : 'Add a quiz'},
                              context_instance = c)

@login_required
def add_question(request, quiz_id):#TODO - make factory!
    quiz = get_object_or_404(models.Quiz, pk=quiz_id)
    if request.user != quiz.creator:
        c = RequestContext(request)
        return render_to_response('quizengine/permission_error.html',
                                  {'page_name': "Permission Error",
                                   'action':
                                   'add a question to a quiz you did not create,',
                                   'quiz': quiz},
                                 
                                  context_instance = c
                                  )
    else: #user is the creator
        if request.method == "POST":
            form = forms.NewQuestionForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                #make the question, and for each answer add it
                q = models.Question.objects.create(question = cd['question'],
                                    value = cd['value'],
                                    creator = request.user,
                                    quiz_id = quiz.pk)
                answer_a = models.Answer.objects.create(answer = cd['answer_a'],
                                         is_correct = cd['a_is_correct'],
                                         question = q)
                answer_b = models.Answer.objects.create(answer = cd['answer_b'],
                                         is_correct = cd['b_is_correct'],
                                         question = q)
                answer_c = models.Answer.objects.create(answer = cd['answer_c'],
                                         is_correct = cd['d_is_correct'],
                                         question = q)
                answer_c = models.Answer.objects.create(answer = cd['answer_d'],
                                         is_correct = cd['d_is_correct'],
                                        question = q)
                c = RequestContext(request)
                new_form = forms.NewQuestionForm()
                return render_to_response("quizengine/add_question.html",
                                          {"prev_question":q,
                                           "page_name":
                                           "Add a question to "+quiz.name,
                                           "form": new_form,
                                           "quiz": quiz},
                                          context_instance = c)
                
        else: #new blank form
            form = forms.NewQuestionForm()
        #stuff
        c = RequestContext(request)
        return render_to_response("quizengine/add_question.html",
                                  {"form":form,
                                   "quiz":quiz},
                                  context_instance = c)

@login_required
def detail(request, quiz_id):
    quiz = get_object_or_404(models.Quiz, pk=quiz_id)
    if request.user == quiz.creator:
        return HttpResponseRedirect('/quiz/%d/stats' %quiz.id)
    quiz_form = forms.take_quiz_factory(quiz)
    if request.method == "POST":
        form = quiz_form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            quiz_attempt = models.QuizAttempt.objects.create(
                student = request.user,
                quiz = quiz)
            for f in cd.keys():
                answer = get_object_or_404(models.Answer, pk=cd[f])
                question = answer.question
                attempt = models.QuestionAttempt(attempt = quiz_attempt,
                                                 question = question,
                                                 response = answer)
                attempt.save()
            return HttpResponseRedirect('/quiz/%d/results/%d/' 
                                        %(int(quiz_id), int(quiz_attempt.pk)
                                          )
                                        )
    else: 
        form = quiz_form()
        c = RequestContext(request)
        return render_to_response("quizengine/take_quiz.html",
                                  {'page_name': quiz.name,
                                   'form':form,
                                   'quiz':quiz},
                                   context_instance = c)

@login_required
def results(request, quiz_id, attempt_id):
    quiz = get_object_or_404(models.Quiz, pk=quiz_id)
    attempt = get_object_or_404(models.QuizAttempt,
                                pk = attempt_id)
    #watch this^ in debugging I'm not sure I'm making the query right here
    question_attempts = attempt.questionattempt_set.all()
    #pull the data we need out
    #return the data needed to create the page
    c = RequestContext(request)
    return render_to_response("quizengine/quiz_results.html",
                              {"page_name" : quiz.name+" Results",
                               "quiz":quiz,
                               "attempt":attempt,
                               "question_attempts":question_attempts},
                              context_instance = c)
                               

                               
                               
@login_required
def stats(request, quiz_id):
    quiz=get_object_or_404(models.Quiz, pk=quiz_id)
    if quiz.creator != request.user:
        c = RequestContext(request)
        return render_to_response('quizengine/permission_error.html',
                                  {'action':
                                   'view the statistics to a quiz you did not create,',
                                   'page_name':'Permission error',
                                   'quiz': quiz},
                                    context_instance = c)
    question_list = []
    #contains this dict for each question
    #{'question':question,
    # 'difficulty':difficulty,
    # 'discriminator': discriminator,
    # 'distractors': [top_distractor, bottom_distractor]
    for question in quiz.question_set.all():
        #Get the Difficulty Index
        total = models.QuestionAttempt.objects.filter(question__exact=question.id)
        correct = total.filter(response__is_correct = True)
        difficulty = correct.count()/total.count()
        #Get the discriminator
        dlist = total.annotate(score=Sum('question__value')).order_by( 'score' )
        
        length = dlist.count()
        top = dlist[:length//2]#possible to lose one student here(fix later)
        bottom = dlist[length//2:length//2]
        discriminator = (
            (dlist.filter(response__is_correct = True)[:length//2].count()/total.count())
            -(dlist.filter(response__is_correct = True)[length//2:length//2].count()/total.count())
            )
        #distractor = []
        #for half in (top, bottom):
        #    
        #    distractor
        question_list.append({'question':question,
                              'difficulty': difficulty,
                              'discriminator':discriminator,
                              #'distractor': distractor,
                              }
                             )
    c = RequestContext(request)
    return render_to_response('quizengine/quiz_stats.html',
                              {'page_name': 'Quiz statistics',
                               'quiz': quiz,
                               'question_list': question_list,
                               },
                              context_instance = c,
                              )
