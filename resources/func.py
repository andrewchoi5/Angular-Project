#!/usr/bin/env python
from webapps.util import httpparser, wsgireader
from datetime import datetime

def getParser(env, readFn=wsgireader.read): # get parser, use WSGI reader by default
  return httpparser.getInstance(env, readFn)

def getMethod(parser):
  return parser.getMethod()

def validateRequestMethod(parser, valid=['GET', 'POST']): # limit to valid actions
  method = parser.getMethod()
  if method not in valid: raise Exception('invalid request method: ' + str(method))

def getRequestData(parser):
  return parser.parse()

def validateRequestData(data, required=[]):
  httpparser.validate(data, required)

def parseRequestData(data, keys=[]):
  parsed = {}
  for key in keys:
    parsed[key] = []
    if key in data:
      if type(data[key]) == str:
        parsed[key] = [x.strip() for x in data[key].split(',')]
      else: parsed[key] = data[key]
  return parsed

def getUser(env):
  return httpparser.getUser(env)

def getBaseURL(parser):
  return wsgireader.getBaseURL(parser.env)

def getURLPath(url):
  items = url.split('/')
  return '/'.join(items[:len(items)-1])

def isInt(value):
  try:
    return int(value)
  except ValueError:
    return False

def getIDs(data, name, delimiter=','):
  if name not in data: return None
  ids = [int(x) for x in data[name].split(delimiter) if isInt(x) != False]
  return ','.join([str(x) for x in ids])

def convertStrToDate(ts):
  if type(ts) not in (str, unicode): return None
  try: # HTTP format
    return datetime.strptime(ts[:19] + ' UTC', '%Y-%m-%dT%H:%M:%S %Z')
  except ValueError:
    try: # Alert format
      return datetime.strptime(ts[:19] + ' UTC', '%Y-%m-%d %H:%M:%S %Z')
    except ValueError: # YYYY-MM-DD format
      return datetime.strptime(ts[:10] + ' UTC', '%Y-%m-%d %Z')
  # Otherwise, not understood

def decode(field, src, encoding):
  return (src[field].decode(encoding) if type(src[field]) == str else src[field]) if field in src else None

def convert(ds, fields, src, encoding):
  for x in fields:
    # convert to Unicode if value is encoded string
    ds[x] = decode(x, src, encoding)
    if x == 'date' and ds['date']: ds['date'] = convertStrToDate(ds['date'])

def isAdmin(dl, user, permission='admin'):
  access = dl.getUserAccess(user)
  return True if access and permission in access and access[permission] > 0 else False

def isReleaseManager(dl, user):
  return isAdmin(dl, user, 'release-manager')