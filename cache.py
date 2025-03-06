# CACHE FOR WORDS
cacheRegistry = [] 
cacheData     = {}

#CONSTANTS
maxCacheSize = 100

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
