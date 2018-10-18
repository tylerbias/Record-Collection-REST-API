import urllib
from google.appengine.api import urlfetch
import json


def get_google_email(access_token):
    auth_url = 'https://www.googleapis.com/plus/v1/people/me'
    accessed_data = urlfetch.fetch(url=auth_url, method=urlfetch.GET, headers={'Authorization': access_token})
    accessed_content = json.loads(accessed_data.content)
    returnedEmail = accessed_content['emails'][0]['value']
    return returnedEmail