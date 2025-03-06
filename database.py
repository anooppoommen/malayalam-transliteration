import sqlite3

schemefile   = sqlite3.connect("ml.scheme")
schemeCrusor = schemefile.cursor()

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
    saveKeyValue(key,values,Tokentype,matchType)
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
def fetchWord(wordID):
  schemeCrusor.execute("select word from wordList where wordid=%d"%(wordID))
  return schemeCrusor.fetchall()
