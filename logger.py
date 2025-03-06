import time

_ER_  = 'ERROR'
_WRN_ = 'WARNING'
_LOG_ = 'LOG'

def addLog(logType,msg):
  logFile = open('log.txt','a',encoding='utf-8')
  logFile.write(logType+' : '+msg+' @ '+time.strftime("%Y-%m-%d %H:%M:%S")+'\n')
  logFile.close()
