import sqlite3
import itertools
import time
from database import setupScheme, saveKeyValue, fetchWord, schemeCrusor, schemefile, extractKeysAndValues
from scheme import createSchemeFile
from tokenizer import generateWordList, flatten, reduceNoise
from learner import learnFromFiles, updateTokenFrequency, reverseTranslate
from cache import cache, getFromCache
from logger import addLog
from ui import ui

createSchemeFile()
learnFromFiles(range(0, 6))

ui()
# ui(['learn'])

