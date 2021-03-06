import glob
import os
import sys

from WriteFile import WriteFile

header = """\
#!/usr/bin/python
#
# Don't edit this file.  Use conf-* for configuration.
#
# Generated by spac, see http://untroubled.org/spac/

import os
import sys

_mtime_cache = { }
def mtime(filename):
	global _mtime_cache
	try:
		m = _mtime_cache[filename]
	except KeyError:
		try:
			m = os.stat(filename)[8]
		except OSError:
			m = -1
		_mtime_cache[filename] = m
	return m

def ne(filename):
	try:
		m = os.stat(filename)[8]
		_mtime_cache[filename] = m
		return 0
	except:
		return 1

def nt(target, deps):
	m = mtime(target)
	for dep in deps:
		if m < mtime(dep):
			return 1
	return 0

def make(target, commands, deps):
	if ne(target) or nt(target, deps):
		for command in commands:
			print '+', command
			if os.system(command) != 0:
				sys.exit(1)

"""

done = { }
def recurse(name, targets, out):
	global done
	target = targets[name]
	for dep in target.dependancies:
		if dep in targets and dep not in done:
			recurse(dep, targets, out)
	newcom = [ ]
	oldcom = target.commands[:]
	oldcom.reverse()
	while oldcom:
		command = oldcom.pop()
		while command[-1] == '\\':
			command = command[:-1] + oldcom.pop()
		command = command.replace('$$', '$')
		newcom.append(command)
	out.write("make(%s, %s, %s)\n" % (repr(name), repr(newcom),
									  repr(target.dependancies)))
	done[name] = 1

def write(targets, filename='make.py'):
	out = WriteFile(filename)
	out.write(header)
	recurse('all', targets, out)
	out.close()
