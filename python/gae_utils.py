import os
import urllib
import logging
import urlparse
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.template import TemplateDoesNotExist

class BaseHandler(webapp.RequestHandler):
    template_values = {};

    def generate(self, content_type='text/html', template_name='index.html'):
        """Supplies a common template generation function.

        When you call generate(), we augment the template variables supplied with
        the current user in the 'user' variable and the current webapp request
        in the 'request' variable.

        The BaseHandler class is based on code from ryanwi's twitteroauth project
        @see: http://github.com/ryanwi/twitteroauth
        """

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

        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', template_name))

        try:
            self.response.out.write(template.render(path, values))
        except TemplateDoesNotExist, e:
            self.response.set_status(404)
            self.response.out.write(template.render(os.path.join('templates', '404.html'), values))

    def set_template_value(self, name, value):
        self.template_values[name] = value;

    def get_param(self, name, default_value, type):
        param = self.request.get(name)
        if '' == param:
            param = default_value
        if 'int' == type:
            param = int(param)
        if 'url' == type:
            if '' == urlparse.urlparse(param).netloc:
                return None
        return param

    def error(self, status_code):
        webapp.RequestHandler.error(self, status_code)
        if status_code == 404:
            self.generate('text/html', '404.html')

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

class HTTP():
    request_url = ''

    headers = {}

    def set_header(self, name, value):
        self.headers[name] = value

    def get_headers(self):
        return self.headers

    def request(self, url, **params):
        if 0 < len(params):
            self.request_url = "%s?%s" % (url, urllib.urlencode(params))
        else:
            self.request_url = url
        try:
            result = urlfetch.fetch(self.request_url)
            if result.status_code == 200:
                return result
            elif result.status_code == 400:
                logging.error('HTTP Status 400: Limit exceeded')
        except:
            logging.error('HTTP Request: Result could not be fetched')
        return None

    def get_request_url(self):
        return self.request_url

class Cache():
    pass