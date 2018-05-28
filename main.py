import sqlite3
import itertools
import time

schemefile   = sqlite3.connect("ml.scheme")
schemeCrusor = schemefile.cursor()

# CACHE FOR WORDS
cacheRegistry = [] 
cacheData     = {}

#CACHE FOR TOKENS     
savedTokens  = {}

#CONSTANTS
maxCacheSize = 100
maxTokenSize = 8

_ER_  = 'ERROR'
_WRN_ = 'WARNING'
_LOG_ = 'LOG'

def addLog(logType,msg):
  logFile = open('log.txt','a',encoding='utf-8')
  logFile.write(logType+' : '+msg+' @ '+time.strftime("%Y-%m-%d %H:%M:%S")+'\n')
  logFile.close()

def cache(pattern,data):
  global cacheRegistry
  global cacheData
  
  if pattern in cacheRegistry:
    cacheRegistry.remove(pattern)
    cacheRegistry.append(pattern)
    return True
  
  if len(cacheRegistry) >= maxCacheSize:
    keyToRemove = cacheRegistry[0]
    cacheRegistry = cacheRegistry[1:]
    del cacheData[keyToRemove]

  cacheRegistry.append(pattern)
  cacheData[pattern] = data
  return True
def getFromCache(pattern):
  if pattern in cacheRegistry:
    return cacheData[pattern]
  return False

def setupScheme():
  schemeCrusor.execute('''
    create table if not exists symbols(
      id integer not null primary key autoincrement,
      pattern varchar(32),
      value1  varchar(32),
      value2  varchar(32),
      value3 varchar(32),
      type integer,
      matchType integer,
      frequency integer default 0
    )
  ''')
        
  schemeCrusor.execute('''
    create table if not exists words(
      id integer not null primary key autoincrement,
      pattern varchar(120),
      wordID integer
    )
  ''')
  schemeCrusor.execute('''
    create table if not exists wordList(
      wordId integer not null primary key autoincrement,
      word varchar(120),
      frequency integer default 0
    )
  ''')
  
  #INDEXES TO SPEED UP QUERY
  schemeCrusor.execute('create index pattern_SYMBOLS on symbols (pattern asc)')
  schemeCrusor.execute('create index pattern_WORDS on words (pattern asc)')
  schemeCrusor.execute('create index wordId_WORDLIST on wordList(wordId asc)')
  schemeCrusor.execute('create index value1_SYMBOLS on symbols (value1 asc)')

  schemefile.commit()
  return True
def extractKeysAndValues(keys,values,Tokentype,matchType=1):
  if str(type(keys)) == "<class 'tuple'>":
    for key in keys:
      if str(type(key)) == "<class 'tuple'>":
        extractKeysAndValues(key,values,Tokentype,2)
      else:
        saveKeyValue(key,values,Tokentype,matchType)
  else:
    saveKeyValue(keys,values,Tokentype,matchType)
def saveKeyValue(key,values,Tokentype,matchType):
  #print(key,values)
  if str(type(values)) == "<class 'list'>":
    if len(values) > 2:
      value1 = values[0]
      value2 = values[1]
      value3 = values[2]
    elif len(values) >1:
      value1 = values[0]
      value2 = values[1]
      value3 = ''
  else:
    value1 = values
    value2 = ''
    value3 = ''

  sql = '''insert into symbols 
      (pattern,value1,value2,value3,type,matchType) 
      values('%s','%s','%s','%s',%d,%d)'''%(key,value1,value2,value3,Tokentype,matchType)
  return schemeCrusor.execute(sql)#,[])
def vowel(hash):
  for hashKey in hash:
    extractKeysAndValues(hashKey,hash[hashKey],1,1)
    schemefile.commit()
def consonants(hash):
  for hashKey in hash:
    extractKeysAndValues(hashKey,hash[hashKey],2,1)
    schemefile.commit()
def generateCV():
  tokensv = []
  tokensc = []
  sqlv = "select pattern,value2 from symbols where type = 1"
  sqlc = "select pattern,value1,value2 from symbols where type=2"
  res = schemeCrusor.execute(sqlv)
  for i in res:
    tokensv.append(i)
  res = schemeCrusor.execute(sqlc)
  for i in res:
    tokensc.append(i)
  for consonant in tokensc:
    consonant_has_inherent_a_sound = (consonant[0][len(consonant[0])-1] == 'a' and  consonant[0][len(consonant[0])-2] != 'a')
    if consonant_has_inherent_a_sound:
      pattern = consonant[0][:len(consonant[0])-1]
      value = consonant[1]+'്'
      saveKeyValue(pattern,value,3,1)
    for v in tokensv:
      if v[1] != '':
        if consonant_has_inherent_a_sound:
          pattern = consonant[0][:len(consonant[0])-1]+v[0]
        else:
          pattern = consonant[0]+v[0]
        values = consonant[1]+v[1]
        saveKeyValue(pattern,values,3,1)
def createSchemeFile():
  setupScheme()
  
  vowel({"~" : "്"})
  vowel({"a" : "അ"})
  vowel({(("a"), "aa", "A")  : ["ആ", "ാ"]})
  vowel({"i" : ["ഇ", "ി"]})
  vowel({("ee", "I", "ii", ("i"))   : ["ഈ", "ീ"]})
  vowel({"u" : ["ഉ", "ു"]})
  vowel({(("u"), "uu", "oo", "U")   : ["ഊ", "ൂ"]})
  vowel({(("ri", "ru"), "R")  : ["ഋ", "ൃ", "ർ"]})
  vowel({"e" : ["എ", "െ"]})
  vowel({("E", ("e"))  : ["ഏ", "േ"]})
  vowel({("ai", "ei")  : ["ഐ", "ൈ"]})
  vowel({"o" : ["ഒ", "ൊ"]})
  vowel({("O", ("o"))  : ["ഓ", "ോ"]})
  vowel({("ou", "au", "ow")  : ["ഔ", "ൌ"]})
  vowel({("OU", "AU", "OW")  : ["ഔ", "ൗ"]})

  consonants({("ka") : "ക"})
  consonants({("kha", ("gha")) : "ഖ"})
  consonants({"ga"  : "ഗ"})
  consonants({("gha", ("kha")) : "ഘ"})
  consonants({("NGa", ("nga")) :  "ങ്ങ"})
  consonants({"cha" : "ച"})
  consonants({("CHa", ("cha", "jha")) : "ഛ"})
  consonants({(("cha")) : "ച്ഛ"})
  consonants({"ja"  : "ജ"})
  consonants({("jha", "JHa") : "ഝ"})
  consonants({(("nja"), "NJa") : "ഞ്ഞ"})
  consonants({("ta", ("tta")) : "റ്റ"})
  consonants({(("da", "ta"), "Ta") : "ട"})
  consonants({(("da", "ta"), "TTa") : "ഠ"})
  consonants({("Da", ("da")) : "ഡ"})
  consonants({(("da"), "DDa") : "ഢ"})
  consonants({("tha", ("ta")) : "ത"})
  consonants({(("tha", "dha"), "thha") : "ഥ"})
  consonants({(("tha", "dha"), "tathha") : "ത്ഥ"})
  consonants({"da" : "ദ"})
  consonants({(("dha"), "ddha") : "ദ്ധ"})
  consonants({"dha" : "ധ"})
  consonants({"pa" : "പ"})
  consonants({("pha", "fa", "Fa") : "ഫ"})
  consonants({"ba" : "ബ"})
  consonants({"bha" : "ഭ"})
  consonants({("va", "wa") : "വ"})
  consonants({("Sa", ("sha", "sa")) : "ശ"})
  consonants({("sa", "za") : "സ"})
  consonants({"ha" : "ഹ"})

  consonants({"nja" : ["ഞ", "ഞ്ഞ"]})
  consonants({"nga" : ["ങ", "ങ്ങ"]})

  consonants({("kra") : "ക്ര"})
  consonants({"gra"  : "ഗ്ര"})
  consonants({("ghra", ("khra")) : "ഘ്ര"})
  consonants({("CHra", ("chra", "jhra")) : "ഛ്ര"})
  consonants({"jra"  : "ജ്ര"})
  consonants({(("dra", "tra"), "Tra") : "ട്ര"})
  consonants({("Dra", ("dra")) : "ഡ്ര"})
  consonants({"Dhra" : "ഢ്ര"})
  consonants({("thra", ("tra")) : "ത്ര"})
  consonants({"dra" : "ദ്ര"})
  consonants({("ddhra", ("dhra")) : "ദ്ധ്ര"})
  consonants({"dhra" : "ധ്ര"})
  consonants({"pra" : "പ്ര"})
  consonants({("phra", "fra", "Fra") : "ഫ്ര"})
  consonants({"bra" : "ബ്ര"})
  consonants({"bhra" : "ഭ്ര"})
  consonants({("vra", "wra") : "വ്ര"})
  consonants({("Sra", ("shra", "sra")) : "ശ്ര"})
  consonants({"shra" : "ഷ്ര"})
  consonants({("sra", "zra") : "സ്ര"})
  consonants({"hra" : "ഹ്ര"})
  consonants({"nthra" : "ന്ത്ര"})
  consonants({(("ndra", "ntra"), "nDra", "Ntra", "nTra") : "ണ്ട്ര"})
  consonants({"ndra" : "ന്ദ്ര"})
  consonants({(("thra"), "THra", "tthra") : "ത്ത്ര"})
  consonants({"nnra" : "ന്ന്ര"})
  consonants({("kkra", "Kra", "Cra") : "ക്ക്ര"})
  consonants({("mpra", "mbra") : "മ്പ്ര"})
  consonants({("skra","schra") : "സ്ക്ര"})
  consonants({"ndhra" : "ന്ധ്ര"})
  consonants({"nmra" : "ന്മ്ര"})
  consonants({("NDra", ("ndra")) : "ണ്ഡ്ര"})

  consonants({("cra") : "ക്ര"})

  consonants({"ya" : "യ"})
  consonants({"sha" : "ഷ"})
  consonants({"zha" : "ഴ"})
  consonants({("xa", ("Xa")) : "ക്സ"})
  consonants({"ksha" : "ക്ഷ"})
  consonants({"nka" : "ങ്ക"})
  consonants({("ncha", ("nja")) : "ഞ്ച"})
  consonants({"ntha" : "ന്ത"})
  consonants({"nta" : "ന്റ"})
  consonants({(("nda"), "nDa", "Nta") : "ണ്ട"})
  consonants({"nda" : "ന്ദ"})
  consonants({"tta" : "ട്ട"})
  consonants({(("tha"), "THa", "ttha") : "ത്ത"})
  consonants({"lla" : "ല്ല"})
  consonants({("LLa", ("lla")) : "ള്ള"})
  consonants({"nna" : "ന്ന"})
  consonants({("NNa", ("nna")) : "ണ്ണ"})
  consonants({("bba", "Ba") : "ബ്ബ"})
  consonants({("kka", "Ka") : "ക്ക"})
  consonants({("gga", "Ga") : "ഗ്ഗ"})
  consonants({("jja", "Ja") : "ജ്ജ"})
  consonants({("mma", "Ma") : "മ്മ"})
  consonants({("ppa", "Pa") : "പ്പ"})
  consonants({("vva", "Va", "wwa", "Wa") : "വ്വ"})
  consonants({("yya", "Ya") : "യ്യ"})
  consonants({("mpa", "mba") : "മ്പ"})
  consonants({("ska","scha") : "സ്ക"})
  consonants({(("cha"), "chcha", "ccha", "Cha") : "ച്ച"})
  consonants({"ndha" : "ന്ധ"})
  consonants({"jnja" : "ജ്ഞ"})
  consonants({"nma" : "ന്മ"})
  consonants({("Nma", ("nma")) : "ണ്മ"})
  consonants({("nJa", ("nja")) : "ഞ്ജ"})
  consonants({("NDa", ("nda")) : "ണ്ഡ"})

  consonants({("ra") : "ര"})
  consonants({(("ra"), "Ra") : "റ"})
  consonants({("na") : "ന"})
  consonants({(("na"), "Na") : "ണ"})
  consonants({("la") : "ല"})
  consonants({(("la"), "La") : "ള"})
  consonants({("ma") : "മ"})

  consonants({("rva", "rwa") : "ര്വ"})
  consonants({"rya" : "ര്യ"})
  consonants({("Rva", "Rwa", ("rva")) : "റ്വ്"})
  consonants({("Rya", ("rya")) : "റ്യ്"})
  consonants({("nva", "nwa") : "ന്വ"})
  consonants({"nya" : "ന്യ"})
  consonants({("Nva", "Nwa", ("nva", "nwa")) : "ണ്വ"})
  consonants({("Nya", ("nya")) : "ണ്യ"})
  consonants({("lva", "lwa") : "ല്വ"})
  consonants({"lya" : "ല്യ"})
  consonants({("Lva", "Lwa", ("lva", "lwa")) : "ള്വ"})
  consonants({("Lya", ("lya")) : "ള്യ"})
  consonants({("mva", "mwa") : "മ്വ"})
  consonants({"mya" : "മ്യ"})
  consonants({'c' : "ക്"})
  
  generateCV()
  
  consonants({
      (("ru")) : "ര്",
      (("r~", "ru")):  "റ്",
      (("nu")): "ന്",
      (("n~", "nu")):  "ണ്",
      (("lu")):  "ല്",
      (("l~", "lu")):  "ള്",
      (("mu")) : "മ്",
      ("r~") : "ര്",
      ("R~") : "റ്",
      ("n~"):  "ന്",
      ("N~") :"ണ്",
      ("l~") : "ല്",
      ("L~"):  "ള്",
      ("m~"):  "മ്",
      "m":  ["ം","ം","മ"],
      "n" :["ൻ", "ന്‍", "ന"],
      ("N", ("n")): ["ൺ", "ണ്‍", "ണ"],
      "l":["ൽ", "ല്‍", "ല"],
      ("L", ("l")) :["ൾ", "ള്‍", "ള"],
      ("r") :["ർ", "ര്‍", "ര"]
  })

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
def fetchWord(wordID):
  schemeCrusor.execute("select word from wordList where wordid=%d"%(wordID))
  return schemeCrusor.fetchall()
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
def ui(opts=[]):
  
  print('TRANSLITERATOR')

  while True:
    
    word =  input("Enter word to transliterate : ")
    wordList = generateWordList(word)

    print('Possible outputs are')

    for i in range(0,len(wordList)):

      if str(type(wordList[i])) == "<class 'tuple'>":
        print("%d %s"%(i,wordList[i][0]))
      else:
        print("%d %s"%(i,wordList[i]))
    
    if 'train' in opts:
      
      index = int(input("Enter the index of exact match : "))
      if index != -1:
        if str(type(wordList[index])) == "<class 'tuple'>":
          wordl = wordList[index][0]
        else:
          wordl = wordList[index]
        
        if isLearnedWord(wordl) == False:        
          learnPatternsFor(wordl)
        else:
          wordId = schemeCrusor.execute("select wordId from wordList where word = '%s' "%(wordl)).fetchall()[0][0]
          schemeCrusor.execute("update words set frequency = frequency+1 where pattern = '%s' and wordId = %d"%(word,wordId))
          schemefile.commit()

        updateTokenFrequency(word,wordl)
        
    elif len(wordList) == 1:
      if str(type(wordList[0])) == "<class 'tuple'>":
        wordl = wordList[0][0]
      else:
        wordl = wordList[0]
      updateTokenFrequency(word,wordl) #IS A CONFIDENT MATCH SHOULD TRAIN ON IT TO IMPROOVE QUALITY

    if input("Convert another Word (n/y) ?") == 'n':
      break

createSchemeFile()
learnFromFiles(range(0,6))

ui()
#ui(['learn'])

