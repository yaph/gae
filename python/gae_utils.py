# -*- coding: utf-8 -*-
import os
import urlparse
import logging
import webapp2
import jinja2
from google.appengine.api import urlfetch


class BaseHandler(webapp2.RequestHandler):
    template_values = {};

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

    def generate(self, content_type='text/html', template_name='index.html'):
        """Supplies a common template generation function."""

        content_type += '; charset=utf-8'
        self.response.headers["Content-Type"] = content_type

        values = {
                  'request': self.request,
                  'host': self.request.host,
                  'page_url': self.request.url,
                  'base_url': self.request.application_url
                  }
        values.update(self.template_values)

        template = self.jinja_env.get_template(template_name)
        self.response.out.write(template.render(self.template_values))

    def set_template_value(self, name, value):
        self.template_values[name] = value;

    def get_param(self, name, default_value, type):
        param = self.request.get(name)
        if '' == param:
            return default_value
        if 'int' == type:
            param = int(param)
        elif 'url' == type:
            if Validate().uri(param) is False:
                return None
        return param

    def error(self, status_code):
        webapp2.RequestHandler.error(self, status_code)
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

    def is_ajax(self):
        return "XMLHttpRequest" == self.request.headers.get("X-Requested-With")


class Validate():
    def uri(self, uri):
        try:
            if urlparse.urlparse(uri).netloc:
                return True
            else:
                return False
        except AttributeError:
            return False


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
