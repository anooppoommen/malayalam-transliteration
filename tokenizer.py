from database import schemeCrusor,schemefile,getFromCache,cache,saveKeyValue
import itertools

#CACHE FOR TOKENS     
savedTokens  = {}

#CONSTANTS
maxTokenSize = 8

def tokenizeWord(word):
  
  tokenList = []
  while len(word)>0:
    
    strbuff  = word[:min(len(word),maxTokenSize)]
    
    while len(strbuff) > 0:
      if strbuff in savedTokens:
        res = savedTokens[strbuff]
        break
      else:
        sql = "select pattern,value1,value2,value3,id,frequency from symbols where pattern = '%s' order by frequency desc"%(strbuff)
        schemeCrusor.execute(sql)
        res = schemeCrusor.fetchall()
        if len(res) == 0:
          strbuff = strbuff[:len(strbuff)-1]
        else:
          savedTokens[strbuff] = res
          break
    else:
      tokenList.append(word[0])
      word = word[1:]
      strbuff = ''

    word = word[len(strbuff):]
    tokenList.append(res)
  
  return tokenList
def reTokenizeWord(mlword):
  tokenList = []

  while len(mlword)>0:
    strbuff = mlword[:min(7,len(mlword))] #6 digits max 
    while len(strbuff)>0:
      #sql = "select pattern from symbols where value1 = '%s' or value2 = '%s' or value3 = '%s'"%(strbuff,strbuff,strbuff)
      if strbuff in savedTokens:
        res = savedTokens[strbuff]
        break
      else:
        sql = "select lower(pattern) as pattern from symbols where value1 = '%s' or value2 = '%s' or value3 = '%s' group by lower(pattern) order by frequency"%(strbuff,strbuff,strbuff)
        schemeCrusor.execute(sql)
        res = schemeCrusor.fetchall()
        if len(res) == 0:
          strbuff = strbuff[:len(strbuff)-1]
          if len(strbuff) == 0:
            return -1
        else:
          savedTokens[strbuff] = res
          break
    mlword = mlword[len(strbuff):]
    tokenList.append(res)

  return tokenList
def getMaxTokenCount(tokenMatrix):
  count = 1
  for i in tokenMatrix:
    count *= len(i)
  return count 

def getLargestMatrixIndex(matrix):
  index = 0
  for i in range(1,len(matrix)):
    if len(matrix[i]) > len(matrix[index]):
      index = i
  return index
def breakPattern(word):
  wordList = []
  while len(word)>0:
    strbuff = word
    while len(strbuff) >0:
      cacheEntry = getFromCache(strbuff)
      if cacheEntry != False:
        wordList.append(cacheEntry)
        break
      else:
        schemeCrusor.execute("select pattern,wordID from words where pattern='%s' order by frequency desc"%(strbuff))
        re = schemeCrusor.fetchall()
        if len(re) ==0:
          strbuff = strbuff[:len(strbuff)-1]
        else:
          w = []
          for ll in re:
            w.append(fetchWord(ll[1])[0][0])
          cache(strbuff,tuple(w))
          wordList.append(tuple(w))
          break
    else:
      break
    word = word[len(strbuff):]
  if len(word) == 0:
    return wordList

  else:
    #wordList should have the closest matches
    #word has remaing part to tokenize
    remList = tokenizeWord(word) #APPLY REDUCE NOISE FUNCTION HERE
    return wordList + remList

  return wordList
def generateWordList(word):  
  re = []
  sql = "select * from words where pattern = '%s' order by frequency desc"%(word)
  schemeCrusor.execute(sql)
  res = schemeCrusor.fetchall()
  if len(res) == 0:
    wordList = flatten(breakPattern(word))
    return (wordList)  
  else:
    for i in res:
      schemeCrusor.execute("select word from wordList where wordID = %d"%(i[2]))
      re += schemeCrusor.fetchall()
    return list(re)
def flatten(tokenList):
  stack = []
  virama = '്'

  for tok in tokenList:
    if str(type(tok)) == "<class 'tuple'>":
      if len(stack) == 0:
        stack = list(tok)
      else:
        ns = []

        #delete virama 
        for el in range(0,len(stack)):
          li = len(stack[el])-1
          if stack[el][li] == virama:
            stack.append(stack[el][:li]) #stack[el] = stack[el][:li]

        for elmt in tok:
          for elms in stack:
            ns.append(elms+elmt)
        stack = ns
    else:
      if len(stack) == 0:
        for elm in tok:
          stack.append(elm[1])
          if elm[2] != '':
            stack.append(elm[2])
          if elm[3] != '':
            stack.append(elm[3])
      else:
        ns = []

        #delete virama end of elms from stack
        for el in range(0,len(stack)):
          li = len(stack[el])-1
          if stack[el][li] == virama:
            stack[el] = stack[el][:li]
  
        for elmt in tok:
          for elms in stack:
            ns.append(elms+elmt[1])
            if elmt[2] != '':
              ns.append(elms+elmt[2])
            if elmt[3] != '':
              ns.append(elms+elmt[3])
        stack = ns
  return list(stack)
def reduceNoise(matrix):
  for m in matrix:
    for i in range(0,len(m)):
      if '~' in m[i][0] and len(m[i]) > 0:
        m.remove(m[i])

  while getMaxTokenCount(matrix) > 100:
    index = getLargestMatrixIndex(matrix)
    if len(matrix[index]) > 1:
      matrix[index] = matrix[index][:len(matrix[index])-1]

  return matrix
