from database import schemeCrusor
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
