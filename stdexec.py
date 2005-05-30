import fnmatch
import glob
import os
import re
import string
import sys
import time

import files

debug = 0

def readlist(filename, dirname=None):
	list = files.readlines(filename)
	if list is None: raise IOError
	if dirname:
		list = map(lambda i,d=dirname:os.path.join(d,i), list)
	#list = map(os.path.normpath, list)
	if debug: print "readlist(%s,%s)=>%s" % (filename,dirname,list)
	return list

_recglob_cache = None

def findfiles(dir):
	list = [ ]
	for file in os.listdir(dir or '.'):
		fullpath = os.path.join(dir, file)
		if os.path.isfile(fullpath):
			list.append(fullpath)
		elif os.path.isdir(fullpath):
			list.extend(findfiles(fullpath))
	return list

def recglob(pattern):
	global _recglob_cache
	if _recglob_cache is None:
		_recglob_cache = findfiles('')
	return filter(lambda f,p=pattern:fnmatch.fnmatch(f,p), _recglob_cache)

def read(filename):
	tmp = files.read(filename)
	if tmp is None and files.copy(filename):
		tmp = files.read(filename)
	return tmp

def fail():
	print 'Execution failed!'
	sys.exit(1)

std_globals = {
	'fail': fail,
	'glob': glob.glob,
	'recglob': recglob,
	'os': os,
	're': re,
	'readlist': readlist,
	'read': read,
	'string': string,
	'time': time,
	}

def stdexec(code, global_env):
	global_env.update(std_globals)
	exec(code, global_env)

def stdexecfile(filename, global_env):
	global_env.update(std_globals)
	return execfile(filename, global_env)
