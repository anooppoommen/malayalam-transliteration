from database import schemeCrusor,schemefile
from tokenizer import tokenizeWord
def isLearnedWord(word):
  sql = "select * from wordList where word ='%s'"%(word)
  schemeCrusor.execute(sql)
  res = schemeCrusor.fetchall()
  if len(res) == 0:
    return False 
  return True 

def sanitizeWordForLearning(word):
  
  word = word.replace('\u200d','')
  word = word.replace('\u200c','')
  word = word.strip()

  return word
def flattenToken(matrix):
  if len(matrix) < 2:
    return matrix
  
  wordsCount = getMaxTokenCount(matrix)
  
  if wordsCount > 50:
    addLog(_WRN_,'%d possiilites with matrix'%(wordsCount)+' '+str(matrix))
    print("%d possibilities for "%(wordsCount),end='')

  matrixA = list(itertools.product(*matrix))
  return matrixA

def reverseTranslate(word):
  tokenList = reTokenizeWord(word)
  if tokenList == -1:
    return -1
  wordsList = flattenToken(tokenList)
  possilePatterns = []
  for i in wordsList:
    q = ''
    for j in i:
      q = q+j[0]
    possilePatterns.append(q)
  return possilePatterns
def learnPatternsFor(word):
  patternList = reverseTranslate(word)
  failedFileList = open('failed.txt','a',encoding ='utf-8')
  if(patternList == -1):
    print("failed to learn word %s"%(word))
    failedFileList.write(word+'\n')
    return -1
  #print(word,'=>',patternList) 
  print('learning %s'%(word))

  schemeCrusor.execute("insert into wordList (word) values('%s')"%(word))
  schemefile.commit()

  schemeCrusor.execute("select wordId from wordList where word = '%s'"%(word))
  d = schemeCrusor.fetchall()
  wordId = d[0][0]
  for i in patternList:
    schemeCrusor.execute("insert into words (pattern,wordId) values('%s','%d')"%(i,wordId))
  schemefile.commit()
def learnFromFiles(fileList):
  for i in fileList:
    learningFile = open("dataset/"+str(i)+'.txt',encoding='utf-8')

    addLog(_LOG_,'learning from file %d.txt Started '%(i))
    
    for word in learningFile:
      word = word.split(' ')[0]
      word = sanitizeWordForLearning(word)
      if isLearnedWord(word):
        print("already learned word %s"%(word))
      else:
        learnPatternsFor(word)
    addLog(_LOG_,'learning from file %d.txt Finished '%(i))
    learningFile.close()

def updateTokenFrequency(pattern,word):
  
  tokenList = tokenizeWord(pattern)
  link = []

  for tokenNode in tokenList:
    
    strbuff = word
    flag    = False

    while len(strbuff)>0:

      for token in tokenNode:
        if strbuff in token[1:4]:
          link.append(token[4])
          flag = True
          break
      
      if flag :
        break
      strbuff = strbuff[:len(strbuff)-1]
    word = word[len(strbuff):]

  for tokenId in link:
    sql = "update symbols set frequency = frequency+1 where id = %d"%(tokenId)
    schemeCrusor.execute(sql)
  schemefile.commit()
  return True
