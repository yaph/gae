#!/usr/bin/env python
#
# GaeBaseHandler class based on
# http://github.com/ryanwi/twitteroauth

import os
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.template import TemplateDoesNotExist

class GaeBaseHandler(webapp.RequestHandler):
  template_values = {};

  """Supplies a common template generation function.

  When you call generate(), we augment the template variables supplied with
  the current user in the 'user' variable and the current webapp request
  in the 'request' variable.
  """
  def generate(self, content_type='text/html', template_name='index.html', **template_values):
    # set the content type
    content_type += '; charset=utf-8'
    self.response.headers["Content-Type"] = content_type

    values = {
      'request': self.request,
      'host': self.request.host,
      'page_url': self.request.url,
      'base_url': self.request.application_url
    }
    values.update(self.template_values)
    values.update(template_values)
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', template_name))
    
    try:
      self.response.out.write(template.render(path, values))

    except TemplateDoesNotExist, e:
      self.response.set_status(404)
      self.response.out.write(template.render(os.path.join('templates', '404.html'), values))

  def set_template_value(self, name, value):
      self.template_values[name] = value;

  def error(self, status_code):
    webapp.RequestHandler.error(self, status_code)
    if status_code == 404:
      self.generate('404.html')

  def get_cookie(self, name):
    return self.request.cookies.get(name)

  def set_cookie(self, name, value, path='/', expires="Fri, 28-Dec-2666 23:59:59 GMT"):
    self.response.headers.add_header(
      'Set-Cookie', '%s=%s; path=%s; expires=%s' %
      (name, value, path, expires))

  def expire_cookie(self, name, path='/'):
    self.response.headers.add_header(
    'Set-Cookie', '%s=; path=%s; expires="Fri, 31-Dec-1999 23:59:59 GMT"' %
    (name, path))