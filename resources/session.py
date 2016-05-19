#!/usr/bin/env python
from webapps.util import documents
from webapps.sml.resources import func
from webapps.sml.lib import common, datalayer

# web entry point ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def application(env, response):
  responsetext = '' # HTTP response text
  status = '200 OK' # HTTP return code and message
  encoding = 'utf-8'
  document = documents.JSONRenderer(None, None, encoding)

  try:
    user = func.getUser(env)
    conf = common.getConfig()
    db = common.getDBConn(conf)
    dl = datalayer.DataLayer(db)
    permissions = { 'user' : user }
    access = dl.getUserAccess(user)
    if access: permissions.update(access)
    document = documents.JSONRenderer(permissions, None, encoding)
  
  except Exception as e:
    document = documents.JSONRenderer({'error' : str(e) }, None, encoding)
  
  finally:
    responsetext = document.render()
    headers = document.getHeaders()    
    headers.append(('Content-Length', str(len(responsetext))))
    headers.append(('Cache-Control', 'no-cache, must-revalidate'))
    # WSGI requirements:
    response(status, headers) # initiate response, incl. HTTP status and headers
    return [responsetext] # return list of strings


# ISAPI entry point for PyISAPIe on IIS; never called in Apache container ~~~~~
def Request():
  import Http.WSGI
  Http.WSGI.RunWSGI(application)