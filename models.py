from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

#######################
#Quiz Structure Models#
#######################

class Quiz(models.Model):
    name = models.CharField(max_length = 255)
    creation = models.DateField(auto_now_add=True)
    creator = models.ForeignKey(User)
    #TODO: Implement a lock
    #TODO: Implement a limit who can take by class

    def __unicode__ (self):
        return self.name

    def possible(self):
        total = 0
        for question in self.question_set.all():
            #question.save() commented out to test something
            total += question.value
        return total


class Question(models.Model):
    question = models.CharField(max_length = 255)
    quiz = models.ForeignKey(Quiz)
    creator = models.ForeignKey(User)
    creation = models.DateField(auto_now_add = True)
    #objective = TODO: include standards linking in later versions
    value = models.IntegerField(default = 1)

    def __unicode__(self):
        return self.question

class Answer(models.Model):
    answer = models.CharField(max_length = 255)
    question = models.ForeignKey(Question)
    is_correct = models.BooleanField(default = False)
    #Creator is tied to the quiz
    def __unicode__(self):
        return self.answer

#TODO: Standards and Classes


##########
#Attempts#
##########
class QuizAttempt(models.Model):
    student = models.ForeignKey(User)
    quiz = models.ForeignKey(Quiz)
    date = models.DateField(auto_now_add = True)
    def score(self):
        total = 0
        for question in self.questionattempt_set.all():
            if question.response.is_correct:#if ya got it right
                total += question.question.value
        return total
    def possible(self):
        return self.quiz.possible()
    ## def save(self, *args, **kwargs):
    ##     for question in self.quiz.question_set.all():
    ##         try:
    ##             q = self.questionattempt_set.get(question=question.id)
    ##         except:
    ##             q = QuestionAttempt(attempt = self,
    ##                                 question = question)
    ##         q.save()
    ##     super(QuizAttempt, self).save(*args, **kwargs) 
        
    def __unicode__(self):
        return self.student.username+" Quiz: "+unicode(self.quiz.id)+" "+unicode(self.date)


class QuestionAttempt(models.Model):
    attempt = models.ForeignKey(QuizAttempt)
    question = models.ForeignKey(Question)
    response = models.ForeignKey(Answer,
                                 null = True)
    def is_correct(self):
        return self.response.is_correct()
    
    def __unicode__(self):
        return unicode(self.question.id)+unicode(self.attempt)

