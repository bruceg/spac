import os
import stat
import string
import sys
import types

_open_stat_cache = { }

def open_stat(name):
	try:
		return _open_stat_cache[name]
	except KeyError:
		try:
			file = open(name)
			result = (file.read(), os.fstat(file.fileno()))
		except IOError:
			result = None
			file = None
	_open_stat_cache[name] = result
	return result

def read(name):
	pair = open_stat(name)
	if pair is None: return
	return pair[0]

def readlines(name):
	pair = open_stat(name)
	if pair is None: return
	file = map(string.rstrip, string.split(pair[0], '\n'))
	if file[len(file)-1] == '':
		file.pop()
	return file

def stat(name):
	pair = open_stat(name)
	if pair is None: return
	return pair[1]

def copy(name):
	tmp = open_stat(os.path.join('files', name))
	if tmp is None: tmp = open_stat(os.path.join(sys.path[0], 'files', name))
	if tmp is None: return
	(file,fstat) = tmp
	
	try:
		cstat = os.stat(name)
		if fstat[8] > cstat[8]:
			print "Warning, file '%s' is older than its source" % name
	except OSError:
		print "Copying in special file '%s'" % name
		open(name, 'w').write(file)
		_open_stat_cache[name] = tmp
	return 1
