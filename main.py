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


# import library os for reading path directory name ..
import os
import datetime

# for routing subdomains
from webapp2_extras import routes

# for logging
import logging


# for working with regular expressions
import re

# to be able to import jinja2 , add to app.yaml
import jinja2
import webapp2

# for storing data in google cloud storage
import logging
import lib.cloudstorage as gcs

from google.appengine.api import app_identity

# for using datastore 
from google.appengine.ext import ndb
from google.appengine.api import images
from base64 import b64encode
from base64 import b64decode

# validate user inputs
# import validate 

# use pygl tools
# import pygltools as pt

# for REST APIs
import urllib
import urllib2
import json

# tell jinja2 where to look for files
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Wldata(ndb.Model):
	"""Models a wielange data objects"""
	created = ndb.DateTimeProperty(auto_now_add=True)
	last_edit = ndb.DateTimeProperty(auto_now_add=True)
	login_fail_last = ndb.DateTimeProperty()
	pygl_uri = ndb.StringProperty()
	password_hash = ndb.StringProperty()
	email = ndb.StringProperty()
	title = ndb.StringProperty()
	text0 = ndb.TextProperty()
	text1 = ndb.TextProperty()
	text2 = ndb.TextProperty()
	comments_active = ndb.BooleanProperty()
	login_fails_consec = ndb.IntegerProperty()		# consecutive login fails
	abuse_report_count = ndb.IntegerProperty()		# count abuse reports
	image_id0 = ndb.StringProperty()
	image_id1 = ndb.StringProperty()
	image_id2 = ndb.StringProperty()
	
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		"""
		problem mit none:
		'NoneType' object has no attribute 'split'
		if 'de' in self.request.headers.get('Accept-Language').split(",")[0]:
			# de
			#template = template + '-de.html'	# not used
			template = template + '-en.html'
		else:
			# en
			template = template + '-en.html'
		"""
		output = self.render_str(template, **kw)
		self.write(output)


class ShowPage(Handler):
	def get(self, requested_uri):
		
		# load page
		requested_id = requested_uri.replace("-","").lower()		#TODO verify
		key = ndb.Key(Pyglpage, requested_id)
		page = key.get()

		if not page:
			self.response.out.write("sorry, pygl-page does not exist")
			return
		
		if (page.pygl_uri != requested_uri):
			self.redirect("/" + page.pygl_uri)
			return
		
		#format text
		page_text_formatted0 = re.sub(r"[a-zA-Z0-9_.+-/:?#@%&$=]+\.[a-zA-Z0-9_.+-/:?#@%&$=]+", pt.format_text_links, page.text0)
		page_text_formatted0 = re.sub(r"\*\*(.*?)\*\*", pt.format_text_center, page_text_formatted0, flags=re.DOTALL)
		page_text_formatted0 = re.sub(r"\*(.*?)\*", pt.format_text_bold, page_text_formatted0, flags=re.DOTALL)
		
		page_text_formatted1 = re.sub(r"[a-zA-Z0-9_.+-/:?#@%&$=]+\.[a-zA-Z0-9_.+-/:?#@%&$=]+", pt.format_text_links, page.text1)
		page_text_formatted1 = re.sub(r"\*\*(.*?)\*\*", pt.format_text_center, page_text_formatted1, flags=re.DOTALL)
		page_text_formatted1 = re.sub(r"\*(.*?)\*", pt.format_text_bold, page_text_formatted1, flags=re.DOTALL)
		
		page_text_formatted2 = re.sub(r"[a-zA-Z0-9_.+-/:?#@%&$=]+\.[a-zA-Z0-9_.+-/:?#@%&$=]+", pt.format_text_links, page.text2)
		page_text_formatted2 = re.sub(r"\*\*(.*?)\*\*", pt.format_text_center, page_text_formatted2, flags=re.DOTALL)
		page_text_formatted2 = re.sub(r"\*(.*?)\*", pt.format_text_bold, page_text_formatted2, flags=re.DOTALL)
		
		#######################
		
		# could cause performance issue, only about 5 writes per seconds
		# possible solution: sharding
		
		# get pageviews
		key = ndb.Key(Pageviews, requested_id)
		page_views = key.get()
		
		# count page view
		page_views.views = page_views.views + 1
			
		# update datastore entry
		page_views.put()
		
		########################
		
		self.render('page', page_title=page.title, page_text0=page_text_formatted0, page_text1=page_text_formatted1, page_text2=page_text_formatted2, comments_active = page.comments_active, page_views=page_views.views, page_created = page.created.date(), page_last_edit = page.last_edit.date(), pygl_uri=page.pygl_uri, image_id0=page.image_id0, image_id1=page.image_id1, image_id2=page.image_id2)
		
		return
		
class MainPage(Handler):
	def get(self):
		# get search text
		display_confirmation_code = self.request.get('q')
		
		#self.response.out.write(self.request.headers.get('Accept-Language'))
		self.render('main.html', display_confirmation_code=display_confirmation_code)
		 
		
app = webapp2.WSGIApplication([
    webapp2.Route(r'/<requested_uri>', handler=ShowPage),
    webapp2.Route(r'/', handler=MainPage),
], debug=True)





