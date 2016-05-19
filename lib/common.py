#!/usr/bin/env python
from webapps.util import config, cred, database

filename = 'C:/python-apps/webapps/cpt/config/config.xml'
  
def unpackCreds(creds):
  return cred.decrypt(creds)
  
def getConfig(filename=filename):
  return config.XMLFileParser(filename)

def getDBConn(conf):
  server = conf.get('database.server')
  name = conf.get('database.name')
  user, pwrd = unpackCreds(conf.get('database.creds'))
  port = int(conf.get('database.port'))
  driver = conf.get('database.driver')
  return database.DBConnection(server, name, user, pwrd, port, driver)