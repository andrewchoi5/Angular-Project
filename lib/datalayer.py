#!/usr/bin/env python

class DataLayer:  
  def __init__(self, db):
    self.db = db

  def processRow(self, row, rows, callback=None):
    if not row: return
    rowObj = {}
    for rowData in row.cursor_description:
      field = rowData[0]
      rowObj[field] = getattr(row, field, None)
    if callback: callback(rowObj)
    else: rows.append(rowObj)
  
  def runSP(self, sp, params=[], callback=None):
    rows = []
    def process(row):
      self.processRow(row, rows, callback)
    sql = 'exec {0} {1}'.format(sp, ','.join(['?' for x in params]))
    self.db.run(sql, params, process)
    return rows
  
  def runSPWithResult(self, sp, params=[]):
    sql = """
      declare @result int;
      exec {0} {1}, @result output;
      select @result as result;
    """.format(sp, ','.join(['?' for x in params]))
    rows = self.db.run(sql, params)
    self.db.commit()
    if len(rows): return rows[0].result
    return None

  def runSelect(self, sql, callback=None, params=[]):
    rows = []
    def process(row):
      self.processRow(row, rows, callback)
    self.db.run(sql, params, process)
    return rows
    
  def getProducts(self, callback=None):
    return self.runSelect('select id, name, fullname from dbo.product', callback)
    
  # ----------------------------------------------
  # The following is taken from SML as a reference
  # ----------------------------------------------

  def getDeliverableByID(self, deliverableid, callback=None):
    return self.runSP('dbo.get_deliverable_by_id', [deliverableid], callback)

  def getDeliverables(self, processids, phaseids, callback=None):
    return self.runSP('dbo.get_deliverables', [processids, phaseids], callback)
  
  def getPhases(self, callback=None):
    return self.runSelect('select id, name from phases where [type]=1', callback)

  def getProcesses(self, callback=None):
    return self.runSelect('select id, name, [description], ordinal from dbo.processes', callback)

  def getProcessOwners(self, callback=None):
    return self.runSelect('select o.name, o.program, m.processid from owners o inner join [process-owners] m on o.id=m.ownerid', callback)
  
  def getReleases(self, callback=None):
    return self.runSelect('select * from release.status_v', callback)

  def getReleaseDeliverables(self, releaseid, processids, phaseids, callback=None):
    return self.runSP('release.get_deliverables', [releaseid, processids, phaseids], callback)

  def getReleaseByID(self, releaseid, callback=None):
    return self.runSelect('select * from release.status_v where id=?', callback, [releaseid])

  def getReleaseDeliverableByID(self, releaseid, deliverableid, callback=None):
    return self.runSP('release.get_deliverable_by_id', [releaseid, deliverableid], callback)

  def setRelease(self, release):
    return self.runSPWithResult('[release].[set]', [release['id'],
      release['name'], release['manager'], release['description'],
      release['updater'], release['product'], release['releasedepartment'], release['start'], release['notes'],
      release['department'], release['sponsor'], release['business_lead'], release['product_category'], release['benefits'], 
      release['financial_investment'], release['resource_effort'], release['business_case'], release['gts_goal'], release['top_project']])

  def setReleaseDeliverable(self, d):
    return self.runSPWithResult('[release].[set_deliverable]',
      [d['release'], d['id'], d['owner'],
       d['program'], d['status'], d['evidence'],
       d['updater'], d['date']])

  def disableRelease(self, releaseid, updater):
    return self.runSPWithResult('[release].[disable]', [releaseid, updater])

  def setReleaseDeliverableStatus(self, d):
    return self.runSPWithResult('[release].[set_deliverable_status]',
      [d['release'], d['id'], d['status'], d['updater']])

  def setReleaseDate(self, release):
    return self.runSPWithResult('[release].[set_date]',
      [release['id'], release['phaseid'], release['date'], release['updater']])

  def getReleaseDeliverablesByOwner(self, releaseid, owner, processids, phaseids, callback=None):
    return self.runSP('release.get_deliverables_by_owner', [releaseid, owner, processids, phaseids], callback)
  
  def getReleaseDeliverablesByProcessOwner(self, releaseid, owner, processids, phaseids, callback=None):
    return self.runSP('release.get_deliverables_by_proc_owner', [releaseid, owner, processids, phaseids], callback)

  def setReleaseDeliverables(self, params):
    return self.runSPWithResult('[release].[set_deliverables]',
      [params['id'], params['owner'], params['phaseids'], params['processids'],
       params['date'], params['evidence'], params['new-owner'],
       params['program'], params['updater'], params['status']])

  def getDeliverablesByOwner(self, owner, callback=None):
    return self.runSP('dbo.get_deliverables_by_owner', [owner], callback)

  def getDeliverablesByProcessOwner(self, owner, callback=None):
    return self.runSP('dbo.get_deliverables_by_proc_owner', [owner], callback)

  def getUserAccess(self, user):
    sql = 'select * from dbo.member_access_v where [user]=?'
    rows = self.runSelect(sql, params=[user])
    return rows[0] if rows else None
  
  def setDeliverable(self, d):
    return self.runSPWithResult('dbo.set_deliverable', [
      d['id'], d['name'], d['description'], d['processid'], d['phaseid'], d['npi'],
      d['owner'], d['program'], d['updater']
    ])

  def disableDeliverable(self, deliverableid, updater):
    return self.runSPWithResult('[dbo].[disable_deliverable]', [deliverableid, updater])

  def setDependency(self, deliverableid, prerequisiteid):
    return self.runSPWithResult('[dbo].[set_dependency]', [deliverableid, prerequisiteid])

  def clearDependency(self, deliverableid, prerequisiteid):
    return self.runSPWithResult('[dbo].[clear_dependency]', [deliverableid, prerequisiteid])

  def setProcess(self, process):
    return self.runSPWithResult('[dbo].[set_process]', [process['id'],
      process['name'], process['description'], process['updater']])

  def setProcessOrdinal(self, process):
    return self.runSPWithResult('[dbo].[set_process_ordinal]', [process['id'],
      process['offset'], process['updater']])
  
  def setProcessOwner(self, process):
    return self.runSPWithResult('[dbo].[set_process_owner]', [process['id'],
      process['owner'], process['program'], process['updater']])

  def deleteProcessOwner(self, process):
    return self.runSPWithResult('[dbo].[delete_process_owner]', [process['id'],
      process['owner'], process['program'], process['updater']])

  def getAtRiskReleaseDeliverables(self, callback=None):
    return self.runSelect('select * from [release].[atrisk_v]', callback)
    
  def getWarningReleaseDeliverables(self, callback=None):
    return self.runSelect('select * from [release].[warning_v]', callback)     
  
  def getReleaseErrors(self, releaseid, callback=None):
    return self.runSelect('select * from release.errors_v where ? is null or releaseid=?', callback, [releaseid, releaseid])

  def getReleaseDependencyErrors(self, releaseid, callback=None):
    return self.runSelect('select * from release.dependency_errors_v where ? is null or releaseid=?', callback, [releaseid, releaseid])

  def setReleaseRequirements(self, releaseid, answerids, updater):
    return self.runSPWithResult('requirements.set_deliverables', [releaseid, answerids, updater])

  def getReleaseRequirements(self, releaseid, callback):
    return self.runSelect('select * from release.answer_map_v where releaseid=?', callback, [releaseid])
  
  def getDeliverablesToDelete(self, releaseid, answerids, callback=None):
    return self.runSP('requirements.get_deliverables_to_delete', [releaseid, answerids], callback)
    
  def getQuestions(self, callback=None):
    sql = """
      select q.id, q.question, a.id as answerid, a.subanswerid, a.answer
      from requirements.questions q inner join requirements.answers a on a.questionid = q.id where q.disabled=0
    """
    return self.runSelect(sql, callback)
    
  def getQuestionsMap(self, callback=None):
    sql = """
      SELECT * FROM requirements.[questions-map]
      WHERE answerid in (
      SELECT id FROM requirements.answers
      WHERE questionid in (select id from requirements.questions where disabled = 0))
    """
    return self.runSelect(sql, callback) # must only return answers for questions which are active

  def disableQuestion(self, questionid):
    return self.runSPWithResult('[requirements].[disable_question]', [questionid])
    
  def setQuestion(self, question):
    return self.runSPWithResult('[requirements].[set_question]', [question['id'], question['question']])
    
  def setAnswer(self, answer):
    return self.runSPWithResult('[requirements].[set_answer]', [answer['id'], answer['answer']])

  def setAnswerMap(self, answerid, deliverableid):
    return self.runSPWithResult('[requirements].[set_deliverable_to_answer]', [answerid, deliverableid])
    
  def deleteAnswerMap(self, answerid, deliverableid):
    return self.runSPWithResult('[requirements].[delete_deliverable_to_answer]', [answerid, deliverableid])
    
  def addAdhocDeliverable(self, releaseid, deliverableid, updater):
    return self.runSPWithResult('[release].[add_deliverable]', [releaseid, deliverableid, updater])
    
  def getDisabledDeliverables(self, callback=None):
    sql = """
      select id, name
      from dbo.deliverables
      where disabled = 1 and versionid = (select MAX(id) from versions)
    """
    return self.runSelect(sql, callback)
    
  def enableDeliverable(self, deliverableid, updater):
    return self.runSPWithResult('[dbo].[enable_deliverable]', [deliverableid, updater])