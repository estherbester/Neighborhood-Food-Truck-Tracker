from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from foodtruck.models import *
from foodtruck.truck import *
from django.core.cache import cache
from django.views.decorators.cache import cache_page


def stop_words(sentence): #to remove "the" from a lot of truck names when listing alphabetically
  stopwords = '''
  the
  this
  '''.split()
  words = sentence.split()
  sentence = []
  for word in words:
    if word.lower() not in stopwords:
      sentence.append(word)
  return u' '.join(sentence)

def ft_stuff(): #context variables in all views
   hoods = Hood.objects.all()
   trucks = Truck.objects.all().extra(select={'real_name': 'lower(real_name)'}).order_by('real_name')
   trucks = sorted(trucks, key= lambda truck: stop_words(truck.real_name))
   main_dict = {'hoods':hoods, 'trucks':trucks}
   return main_dict

@cache_page(60*1)  
def food_truck(request):
   try:  
     data = get_all_tweets()
   except: 
     raise Http404
   page_dict = ft_stuff()
   page_dict['tweets'] = data
   t = loader.get_template('foodtruck/foodtruck.html')
   c = Context(page_dict)
   return HttpResponse(t.render(c))

@cache_page(60*1)
def hood_truck(request, hood):
  data = cache.get((('filtered_%s' % str(hood))),filter_trucks(hood))
  page_dict = ft_stuff()
  page_dict['tags'] = data['tags']
  page_dict['hood'] = data['hood']
  page_dict['tweets'] = data['tweets']
  t = loader.get_template('foodtruck/hoodtrucks.html')
  c = Context(page_dict)
  return HttpResponse(t.render(c))     
