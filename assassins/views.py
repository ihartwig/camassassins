from django import http
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template import TemplateDoesNotExist

def staticPage(request, page_name):
  template_name = ''
  if (not page_name):
    template_name = 'staticpage/index.html'
  else: 
    template_name = 'staticpage/' + page_name + '.html'
  try:
    return render(request, template_name)
  except TemplateDoesNotExist:
    raise http.Http404
