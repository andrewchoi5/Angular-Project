#!/usr/bin/env python
from webapps.util import documents, formatters
import pprint

class AbstractDocBuilder():
  def __init__(self, allphases, ownersByProcess, baseurl=None, encoding='utf-8'):
    self.allphases = allphases
    self.ownersByProcess = ownersByProcess
    self.baseurl=baseurl
    self.encoding=encoding
    self.setup()

  def setup(self):
    raise NotImplementedError('{0} not implemented in {1}'.format(method, self.__class__.__name__))

  def add(self, row):
    raise NotImplementedError('{0} not implemented in {1}'.format(method, self.__class__.__name__))
  
  def getdoc(self):
    raise NotImplementedError('{0} not implemented in {1}'.format(method, self.__class__.__name__))


class DefaultDocBuilder(AbstractDocBuilder):
  def setup(self):
    self.processes = {}
    self.phases = {}
    self.deliverables = []
  
  def add(self, row):
    if not row: return
    self.deliverables.append(row)
    index = len(self.deliverables) - 1
    if row['processid'] not in self.processes:
      self.processes[row['processid']] = {
        'name' : row['process'],
        'phases' : {},
        'owners' : self.ownersByProcess[row['processid']] if row['processid'] in self.ownersByProcess else {},
        'ordinal' : row['ordinal']
      }
    if row['phaseid'] not in self.processes[row['processid']]['phases']:
      self.processes[row['processid']]['phases'][row['phaseid']] = []
    self.processes[row['processid']]['phases'][row['phaseid']].append(index)
    if row['phaseid'] not in self.phases: self.phases[row['phaseid']] = row['phase']

  def getResult(self):
    return {
      'processes'    : self.processes,
      'phases'       : self.phases,
      'deliverables' : self.deliverables
    }

  def getdoc(self):
    return documents.JSONRenderer(self.getResult(), None, self.encoding)

  def getProcessOrder(self):
    ordinals = {}
    for x in self.processes:
      ordinals[self.processes[x]['ordinal']] = x
    return ordinals


class TextDocBuilder(DefaultDocBuilder):
  def getdoc(self):
    return documents.TextRenderer(pprint.pformat(self.getResult()), None, self.encoding)


class CSVDocBuilder(AbstractDocBuilder):
  def getFields(self):
    return [
      'name', 'id', 'description', 'process', 'processid', 'phase', 'phaseid',
      'process-owners', 'ordinal', 'owner', 'function', 'npi'
    ]

  def setup(self):
    self.formatter = formatters.CSVFormatter(self.encoding)
    self.formatter.new(None, self.getFields())

  def add(self, row):
    if not row: return
    row['process-owners'] = ', '.join(self.ownersByProcess[row['processid']].keys()) \
      if row['processid'] in self.ownersByProcess else ''
    self.formatter.add(row)

  def getdoc(self):
    return self.formatter.asDoc('deliverables')


class HTMLDocBuilder(DefaultDocBuilder):
  def getTitle(self):
    return 'SML Deliverables'

  def getLink(self):
    return '/deliverable.py?'

  def encode(self, text):
    return documents.entitify(text, self.encoding)

  def getdoc(self):
    if not self.deliverables: raise Exception('no deliverables found')
    
    def enc(text):
      return self.encode(text)
    
    phases = sorted(self.allphases.keys())
    nphases = len(phases)
    colwidth = str(100.0 / float(nphases+1))
    processes = sorted(self.processes.keys())
    ndeliverables = len(self.deliverables)
    
    title = self.getTitle()
    url = self.baseurl + self.getLink()
    elements = [
      '<table><caption>{0}</caption>'.format(enc(title)) +
      '<thead><tr><th rowspan="2" style="width:{0}%">Processes</th><th colspan="{1}">Phases</th></tr>'.format(colwidth, str(nphases)) +
      '<tr><th style="width:{0}%">'.format(colwidth) +
      '</th><th style="width:{0}%">'.format(colwidth).join([enc(self.allphases[x]) for x in phases]) +
      '</th></tr>' + '</thead><tbody>'
    ]
    
    # get process order
    ordinals = self.getProcessOrder()
    
    #for processid in processes:
    for ordinal in sorted(ordinals):
      processid = ordinals[ordinal]
      process = self.processes[processid]
      owners = self.ownersByProcess[processid].keys() if processid in self.ownersByProcess else []
      nowners = len(owners)
      ownerlist = ''
      if nowners == 1:
        ownerlist = '<p>Owner: {0}{1}</p>'.format(enc(owners[0]),
          ' (' + enc(', '.join(self.ownersByProcess[processid][owners[0]])) + ')' \
          if self.ownersByProcess[processid][owners[0]] else '')
      elif nowners > 1:
        ownerlist = '<p>Owners:</p><ul>{0}</ul>'.format(''.join(['<li>' + enc(x) + \
          ' (' + enc(', '.join(self.ownersByProcess[processid][x])) + ')' \
          if self.ownersByProcess[processid][x] else '' + \
          '</li>' for x in owners]))
      elements.append('<tr><td><p>' + enc(process['name']) + '</p>' + ownerlist + '</td>')
      for phaseid in phases:
        if phaseid not in process['phases'] or not process['phases'][phaseid]:
          elements.append('<td>&nbsp;</td>')
          continue
        elements.append('<td><ol>')
        for index in sorted(process['phases'][phaseid]):
          if index >= ndeliverables: continue # should not happen
          link = url + 'id={0}&amp;format=html'.format(str(self.deliverables[index]['id']))
          elements.append('<li><a href="{0}">{1}</a></li>'.format(link, enc(self.deliverables[index]['name'])))
        elements.append('</ol></td>')
      elements.append('</tr>')
    
    elements.append('</tbody></table>')
    
    return documents.HTMLRenderer('\n'.join(elements), title, self.encoding)

  
def getDocBuilder(fmt):
  rendererMap = {
    'json' : DefaultDocBuilder,
    'text' : TextDocBuilder,
    'csv'  : CSVDocBuilder,
    'html' : HTMLDocBuilder
  }
  return rendererMap[fmt] if fmt in rendererMap else DefaultDocBuilder


class AbstractDeliverableDocBuilder(AbstractDocBuilder):
  def __init__(self, ownersByProcess, baseurl=None, urlpath=None, encoding='utf-8'):
    self.ownersByProcess = ownersByProcess
    self.baseurl=baseurl
    self.urlpath=urlpath
    self.encoding=encoding
    self.setup()

  def setResult(self, result):
    pass

class DefaultDeliverableDocBuilder(AbstractDeliverableDocBuilder):
  def setup(self):
    self.result = { 'requires' : [], 'required-by' : []}

  def add(self, row):
    if not row: return
    deliverable = row.copy()
    deliverable['owners'] = self.ownersByProcess[row['processid']] if row['processid'] in self.ownersByProcess else {}
    # fix when UI is updated:
    deliverable['process-owners'] = deliverable['owners']
    dtype = deliverable.pop('type')
    if dtype == 'deliverable':
      self.result.update(deliverable)
    elif dtype in self.result:
      self.result[dtype].append(deliverable)

  def getdoc(self):
    return documents.JSONRenderer(self.result, None, self.encoding)

  def setResult(self, result):
    self.result['result'] = result


class TextDeliverableDocBuilder(DefaultDeliverableDocBuilder):
  def getdoc(self):
    return documents.TextRenderer(pprint.pformat(self.result), None, self.encoding)


class CSVDeliverableDocBuilder(CSVDocBuilder):
  def __init__(self, ownersByProcess, baseurl=None, urlpath=None, encoding='utf-8'):
    self.ownersByProcess = ownersByProcess
    self.baseurl=baseurl
    self.urlpath=urlpath
    self.encoding=encoding
    self.setup()  

  def getFields(self):
    return [
      'type', 'name', 'id', 'description', 'process', 'processid', 'phase',
      'phaseid', 'process-owners', 'ordinal', 'owner', 'function', 'npi'
    ]

  def getdoc(self):
    return self.formatter.asDoc('deliverable-details')


class HTMLDeliverableDocBuilder(AbstractDeliverableDocBuilder):
  def getLink(self):
    return self.urlpath + '/model.py?format=html'

  def getSelfLink(self):
    return self.baseurl + '?'
  
  def setup(self):
    self.data = { 'deliverable' : [], 'requires' : [], 'required-by' : [] }

  def add(self, row):
    if not row or not 'type' in row: return
    if row['type'] in self.data: self.data[row['type']].append(row)

  def getdoc(self):
    deliverable = self.data['deliverable'][0] if self.data['deliverable'] else None
    if deliverable == None: raise Exception('no deliverable data found')
    
    def enc(text):
      return documents.entitify(text, self.encoding)
    
    resourceURL = self.getLink()
    
    title = '{0} [{1}]'.format(enc(deliverable['name']), enc(deliverable['id']))
    elements = ['<table><caption>{0}</caption>'.format(title) +
                '<thead><tr><th>Details</th><th>Requires</th><th>Required By</th></tr></thead><tbody><tr>']
    
    # deliverable cell
    elements.append('<td style="width: 33.3%">')
    if deliverable['description']: elements.append('<p>{0}</p>'.format(enc(deliverable['description']).replace('\n', '<br/>')))    
    for x in ['process', 'phase']:
      elements.append('<p><b>{0}</b>: {1} [{2}]</p>'.format(x.title(), enc(deliverable[x]), enc(deliverable[x + 'id'])))
    processid = deliverable['processid']
    
    if deliverable['owner']:
      owner = '<p><b>Owner</b>: {0}{1}</p>'.format(enc(deliverable['owner']), \
              ' (' + enc(deliverable['function']) + ')' if deliverable['function'] else '')
      elements.append(owner)
    
    owners = self.ownersByProcess[processid].keys() if processid in self.ownersByProcess else []
    nowners = len(owners)
    if nowners == 1:
      ownerlist = elements.append('<p><b>Process Owner</b>: {0}{1}</p>'.format(enc(owners[0]),
        ' (' + enc(', '.join(self.ownersByProcess[processid][owners[0]])) + ')' \
        if self.ownersByProcess[processid][owners[0]] else ''))
    elif nowners > 1:
      ownerlist = elements.append('<p><b>Process Owners</b>:</p><ul>{0}</ul>'.format(''.join(['<li>' + enc(x) + \
        ' (' + enc(', '.join(self.ownersByProcess[processid][x])) + ')' \
        if self.ownersByProcess[processid][x] else '' + \
        '</li>' for x in owners])))
    
    # release stuff
    if 'status' in deliverable and deliverable['status']:
      elements.append('<p><b>Status</b>: {0}</p>'.format(enc(deliverable['status'])))
    
    if 'evidence' in deliverable and deliverable['evidence']:
      elements.append('<p><b>Evidence</b>: {0}</p>'.format(enc(deliverable['evidence'])))
    
    if 'date' in deliverable and deliverable['date']:
      elements.append('<p><b>Date</b>: {0}</p>'.format(enc(deliverable['date'].isoformat(' ')[:10])))
    
    elements.append('</td>')
    
    # remaining cells
    for x in ['requires', 'required-by']:
      elements.append('<td style="width: 33.3%">')
      if self.data[x]:
        elements.append('<ul>')
        for d in self.data[x]:
          link = self.getSelfLink() + 'id={0}&amp;format=html'.format(d['id'])
          processLink = resourceURL + '&amp;process={0}'.format(str(d['processid']))
          phaseLink = resourceURL + '&amp;phase={0}'.format(str(d['phaseid']))
          elements.append(
            '<li><a href="{0}">{1}</a>&nbsp;[{2}] / process:&nbsp;<a href="{3}">{4}</a>&nbsp;[{5}] / phase:&nbsp;<a href="{6}">{7}</a>&nbsp;[{8}]</li>'.format(
                link, enc(d['name']), enc(d['id']), processLink, enc(d['process']), enc(d['processid']),
                phaseLink, enc(d['phase']), enc(d['phaseid'])
              )
            )
        elements.append('</ul>')
      else:
        elements.append('[None]')
      elements.append('</td>')
    
    elements.append('</tr></tbody></table>')
    
    return documents.HTMLRenderer(''.join(elements), title, self.encoding)

  
def getDeliverableDocBuilder(fmt):
  rendererMap = {
    'json' : DefaultDeliverableDocBuilder,
    'text' : TextDeliverableDocBuilder,
    'csv'  : CSVDeliverableDocBuilder,
    'html' : HTMLDeliverableDocBuilder
  }
  return rendererMap[fmt] if fmt in rendererMap else DefaultDeliverableDocBuilder