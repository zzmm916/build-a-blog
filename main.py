#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("frontpage.html", blogs=blogs)

    #def get(self):
        #self.render_front()

class Newpost(Handler):
    def render_front(self, title="", body="", error=""):
        self.render("newpost.html", title=title, body=body, error=error)
        # t = jinja_env.get_template("newpost.html")
        # content = t.render(title=title, body=body, error=error)
        # self.response.write(content)
    def get(self):
        self.render_front()
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = Blog(title=title, body=body)
            post.put()
            id= post.key().id()
            self.redirect("/blog/%s" % id)
        else:
            error= "we need both a title and body!"
            self.render_front(title, body, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post=Blog.get_by_id(int(id))
        if post:
            t=jinja_env.get_template("post.html")
            content= t.render(post=post)
        else:
            error="there is no post with %s" % id
            t=jinja_env.get_template("post.html")
            content= t.render(error=error)
        self.response.write(content)




app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', Newpost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
