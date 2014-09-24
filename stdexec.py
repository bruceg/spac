import fnmatch
import glob
import os
import re
import sys
import time

import files
import rules

debug = 0

def readlist(filename, dirname=None):
	list = files.readlines(filename)
	if list is None: raise IOError
	if dirname:
		list = [ os.path.join(dirname, i) for i in list ]
	#list = map(os.path.normpath, list)
	if debug: print("readlist(%s,%s)=>%s" % (filename,dirname,list))
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
	return list(filter(lambda f,p=pattern:fnmatch.fnmatch(f,p), _recglob_cache))

def read(filename):
	tmp = files.read(filename)
	if tmp is None and files.copy(filename):
		tmp = files.read(filename)
	return tmp

def fail():
	print('Execution failed!')
	sys.exit(1)

rx_include = re.compile(r'^\s*#\s*include\s+([<"])([^">]+)[">]\s*$', re.MULTILINE)
def scan_cpp(filename,already=None):
	if not already:
		already = { }
	if filename in already:
		return
	if files.copy(filename) or rules.match(filename):
		return [ filename ]
	already[filename] = None
	path = os.path.split(filename)[0]
	file = read(filename)
	if file is None:
		raise IOError
	deps = [ filename ]
	match = rx_include.search(file)
	build_incpaths = files.readlines('build-includes') or [ ]
	incpaths = [ '', path ] + build_incpaths
	while match:
		inctype,inc = match.groups()
		incs = [ ] if inctype == '<' else [ inc ]
		for incpath in incpaths:
			try:
				incs = scan_cpp(os.path.join(incpath, inc), already)
			except IOError:
				continue
			if incs is not None:
				break
		deps.extend(incs or [ ])
		match = rx_include.search(file, match.end())
	return deps

def scan_libs(filename):
	sources = readlist(filename)
	def sourcepath(object, dir=os.path.split(filename)[0]):
		if object[-4:] == '.lib' \
			   or object.find('/') >= 0:
			return os.path.normpath(object)
		return os.path.join(dir, object)
	options = [ s for s in sources if s[0] == '-' ]
	for option in options:
		sources.remove(option)
	sources = [ sourcepath(s) for s in sources ]
	dotlibs = [ "`cat %s`" % s for s in sources if s[-4:] == '.lib' ]

	return (
		sources,
		' '.join([ s for s in sources if s[-4:] != '.lib' ]),
		' '.join(options),
		' '.join(dotlibs)
		)

std_globals = {
	'fail': fail,
	'glob': glob.glob,
	'recglob': recglob,
	'os': os,
	're': re,
	'readlist': readlist,
	'read': read,
	'scan_cpp': scan_cpp,
	'scan_libs': scan_libs,
	'time': time,
	}

def stdexec(code, global_env):
	global_env.update(std_globals)
	exec(code, global_env)

def stdexecfile(filename, global_env):
	global_env.update(std_globals)
	return exec(compile(open(filename).read(), filename, 'exec'), global_env)
