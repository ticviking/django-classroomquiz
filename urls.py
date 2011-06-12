from django.conf.urls.defaults import *


urlpatterns = patterns ('quizengine.views',
                        (r'^$', 'index'),
                        (r'^(?P<quiz_id>\d+)/$', 'detail'),
                        (r'^(?P<quiz_id>\d+)/results/(?P<attempt_id>\d+)/$', 'results'),
                        (r'^(?P<quiz_id>\d+)/stats/$', 'stats'),
                        (r'^add/$', 'add_quiz'),
                        (r'^(?P<quiz_id>\d+)/add/$', 'add_question'),
                        )#TODO: Edit Questions, List all my quizzes
