// global flag so they can't hammer away at the button
var timelineLoading = false;

if (typeof AjaxRequest == 'undefined') alert('AjaxRequest class not found');

var SML = {
  
// Change to match project root directory on host web server
baseUrl: '/sml/',
mimeType: 'application/json',
responseDelimiter: '',  // '--STARTDATA--',

evaluate: function(response) // John + Steve's code to process JSON response
{
  var startLocation = response.indexOf(SML.responseDelimiter);
  
  // if the data never started we have no response to process
  if (startLocation < 0)
  {
    throw new Error('No response found, server responded with: ' + response);
  }
  
  var startDataLocation = startLocation + SML.responseDelimiter.length;
  
  // if there was something before the start of the data, alert on it
  if (startLocation > 0)
  {
    SML.warningHandler('Additional data in server response: ' +
                                response.substring(0, startLocation)); 
  }
  
  // before eval-ing, trim anything before the start of the actual data
  return eval('(' + response.substring(startDataLocation) + ')');
},

checkAdmin: function(clientCallback, adminpage)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/session/' ,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(SML.evaluate(response.responseText), adminpage);
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getDisabled: function(clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/disabled-deliverables.py' ,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

enableDeliverable: function(method, data, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/disabled-deliverables.py',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: false,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

getQuestions: function(clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/question.py' ,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getAnswers: function(releaseID, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release-requirements.py?release=' + releaseID,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getDeliverablesToBeDeleted: function(method, data, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release-requirements.py',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: false,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

setAnswersForRelease: function(method, data, release, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/release-requirements.py',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(release, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: false,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

setQuestion: function(method, data, question, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/question.py',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(question, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: false,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

getAll: function(clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/slice/' ,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getAllReleases: function(clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release/' ,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getRelease: function(id, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release/' + id,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getReleaseErrors: function(id, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release-errors/' + id,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getReleaseOwner: function(id, owner, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/slice/owner/' + owner,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, owner, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getReleasePrime: function(id, owner, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release/' + id + '/owner/' + owner,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, owner, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getReleaseProcessOwner: function(id, owner, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release/' + id + '/process-owner/' + owner,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, owner, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getReleaseProcess: function(releaseID, processID, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release/' + releaseID + '/process/' + processID,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(releaseID, processID, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getReleasePhase: function(releaseID, phaseID, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release/' + releaseID + '/phase/' + phaseID,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(releaseID, phaseID, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getReleasePhaseProcess: function(releaseID, phaseID, processID, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release/' + releaseID + '/process/' + processID + '/phase/' + phaseID,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(releaseID, phaseID, processID, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getReleaseDeliverable: function(releaseID, deliverableID, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/release/' + releaseID + '/deliverable/' + deliverableID,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(releaseID, deliverableID, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

//USED FOR BULK EDIT
getReleaseOwnerPhaseProcess: function(releaseID, selectedOwner, phaseID, processID, source, clientCallback)
{
	//logic to determine which to include in the call
	
	var owner = '';
	if (selectedOwner != '')
		owner = '/owner/' + selectedOwner;
	
	var phase = '';
	if (phaseID != 'All')  // this could be made into something more generic (not numeric)
		phase = '/phase/' + phaseID;
		
	var process = '';
	if (processID != 'All')
		process = '/process/' + processID;
	
  var request = {
    url: SML.baseUrl + 'ws/release/' + releaseID + owner + phase + process,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(releaseID, source, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getPhaseProcess: function(phaseID, processID, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/slice/process/' + processID + '/phase/' + phaseID,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(phaseID, processID, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getDeliverable: function(id, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/deliverable/' + id,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getProcess: function(id, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/slice/process/' + id,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getProcesses: function(id, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/process/',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getPhase: function(id, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/slice/phase/' + id,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(id, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getOwner: function(owner, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/slice/owner/' + owner,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback("Deliverable", owner, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

getProcessOwner: function(owner, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws/slice/process-owner/' + owner,
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback("Process", owner, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
      
    method: 'get',
    
    headers:
      {
        'Accept' : SML.mimeType
      }
  };
  
  SML.send(request);
},

setDeliverable: function(method, data, deliverable, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/set-deliverable',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(deliverable, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: false,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

setProcess: function(method, data, process, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/set-process',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(process, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: false,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

saveRelease: function(method, data, page, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/set-release',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(page, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: false,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

deleteRelease: function(method, data, page, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/set-release',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(page, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: false,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

updateDeliverable: function(method, data, page, clientCallback)
{
  var request = {
    url: SML.baseUrl + 'ws-protected/set-release-deliverable',
				 
    callback:
      function(response)
      {
        if (response.status != 200)
          return SML.errorHandler('HTTP code: ' + response.status);
          
        try
        {
          clientCallback(page, SML.evaluate(response.responseText));
          return true;
        }
        catch (e)
        {
          return SML.errorHandler(e.message);
        }
      },
    method: method,
    async: true,
    data: data,    
    headers:
      {
        'Accept' : SML.mimeType/*,
        'If-None-Match' : SML.generateRequestID()*/
      }
  };
  
  SML.send(request);
},

send: function(request)
{
  var requestor = new AjaxRequest(request);
  requestor.exec();  
},

errorHandler: function(e)
{
  alert('SML error: ' + e);
  return false;
},

warningHandler: function(e)
{
  alert('SML warning: ' + e);
},

enumerate: function(object)
{
  if (typeof(object) !== 'object') { return 'not an object'; }
  var result = new Array();
  for (var i in object) { result.push(i); }
  return result.join('\t');
}
  
};