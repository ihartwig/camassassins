from django import http
from django.core.urlresolvers import reverse


def staticPage(request, page_name):
  return http.HttpResponse('<html><body>'+page_name+'</body></html>')