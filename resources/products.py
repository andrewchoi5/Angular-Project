#!/usr/bin/env python
from webapps.util import documents, formatters
from webapps.sml.lib import common, datalayer
from webapps.sml.resources import func
import pprint

def processGet(dl, data, baseurl, encoding, user):
  fmt = data['format'].lower() if 'format' in data else None
 
  questions = {}
  answers = {}
  
  # build up the questions and answers
  def addQuestion(row):
    if not row: return
    qid = row['id']
    q = row['question']
    aid = row['answerid']
    subanswer = row['subanswerid']
    answer = row['answer']
    
    if qid not in questions: questions[qid] = {'question' : q, 'answers' : []}
    questions[qid]['answers'].append(aid)
    
    answers[aid] = {'deliverables' : [], 'answer' : answer, 'subanswer' : subanswer}

  # add deliverables mapped to each answer
  def addDeliverable(row):
    if not row: return
    aid = row['answerid']
    did = row['deliverableid']
    answers[aid]['deliverables'].append(did)

  dl.getQuestions(addQuestion)
  dl.getQuestionsMap(addDeliverable)
  
  json = {'questions': questions, 'answers': answers}
  if 'result' in data:
    json['result'] = data['result']
  
  return documents.JSONRenderer(json, None, encoding) if not fmt or fmt == 'json' \
    else documents.TextRenderer(pprint.pformat({'questions': questions, 'answers': answers}), None, encoding)

def processPut(dl, data, baseurl, encoding, user):
  if not user or not func.isAdmin(dl, user): raise Exception('user not authorized')
  id = int(data['id']) if 'id' in data else None
  question = data['question'] if 'question' in data else None
  answerid = int(data['answerid']) if 'answerid' in data else None
  answer = data['answer'] if 'answer' in data else None
  deliverableid = int(data['deliverableid']) if 'deliverableid' in data else None
  
  question = { 'id' : id, 'question' : question }
  answer = { 'id' : answerid, 'answer' : answer }
  result = None
  # return documents.TextRenderer(pprint.pformat(question), None, encoding)
  
  # set mapping
  if 'deliverableid' in data:
    result = dl.setAnswerMap(answerid, deliverableid)
    data['result'] = result

  # set answer
  elif 'answerid' in data:
    func.convert(answer, ['answer'], data, encoding)
    result = dl.setAnswer(answer)
    data['result'] = result # update with ID from db (for new answers)  
    
  # set question
  else:
    func.convert(question, ['question'], data, encoding)
    result = dl.setQuestion(question)
    data['result'] = result # update with ID from db (for new questions)
  
  if result == None or result < 0: raise Exception('could not set question; return code {0}'.format(str(result)))
  return processGet(dl, data, baseurl, encoding, user)

def processDelete(dl, data, baseurl, encoding, user):
  if not user or not func.isAdmin(dl, user): raise Exception('user not authorized')
  qid = int(data['questionid']) if 'questionid' in data else None
  aid = int(data['answerid']) if 'answerid' in data else None
  did = int(data['deliverableid']) if 'deliverableid' in data else None
  
  fmt = data['format'].lower() if 'format' in data else None
  
  # delete question
  if 'questionid' in data:
    result = dl.disableQuestion(qid)
    data['result'] = result # update with ID from db
  
  # delete answer deliverable map
  elif 'answerid' in data and 'deliverableid' in data:
    result = dl.deleteAnswerMap(aid, did)
    data['result'] = result # update with ID from db
    
  if result == None or result < 0: raise Exception('could not set question; return code {0}'.format(str(result)))
  return processGet(dl, data, baseurl, encoding, user)



# web entry point ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def application(env, response):
  responsetext = '' # HTTP response text
  status = '200 OK' # HTTP return code and message
  encoding = 'utf-8'
  document = documents.JSONRenderer(None, None, encoding)
  data = {}

  try:
    parser = func.getParser(env)
    func.validateRequestMethod(parser, ['GET', 'PUT', 'DELETE'])
    data = func.getRequestData(parser)
    method = func.getMethod(parser)
    user = func.getUser(env)
    
    conf = common.getConfig()
    db = common.getDBConn(conf)
    dl = datalayer.DataLayer(db)
    
    baseurl = func.getURLPath(func.getBaseURL(parser))
    
    methodMap = { 'GET' : processGet, 'DELETE' : processDelete, 'PUT' : processPut }
    if method not in methodMap: raise Exception('unknown method: {0}'.format(method)) # should not happen
    document = methodMap[method](dl, data, baseurl, encoding, user)
  
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