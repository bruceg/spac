import glob
import os
import string
import sys

from WriteFile import WriteFile
import files
import makefile
import rules

ALL = intern('all')
TOP = intern('TOP')
DEFAULT = intern('DEFAULT')

# Global 
opt_debug = 0
targets = { }
missing = [ ]
srcfiles = [ ]
autofiles = [ 'Makefile', 'AUTOFILES', 'SRCFILES', 'TARGETS' ]

def split_ext(filename, div='.'):
	try:
		i = string.rindex(filename, div)
		return (filename[:i], filename[i+1:])
	except ValueError:
		return (filename, None)

def debug(*str):
	global opt_debug
	if opt_debug:
		print 'debug:', string.join(str, ' ')

class Target:
	def __init__(self, dependancies = None, commands = None):
		self.dependancies = dependancies or [ ]
		self.commands = commands or [ ]

		self.add_dependancy = self.dependancies.append
		self.add_dependancies = self.dependancies.extend
		self.add_command = self.commands.append
		self.add_commands = self.commands.extend
	def __str__(self):
		cmds = string.join(map(lambda line:"\t%s\n"%line, self.commands), '')
		return "%s\n%s" % (string.join(self.dependancies, ' '), cmds)
	def __repr__(self):
		return "Target(%s, %s)" % (self.dependancies, self.commands)

def target(name, deplist, commands):
	global targets
	targets[name] = Target(deplist, commands)
	debug("target(%s) = %s" % (name, repr(targets[name])))

def recurse_dep(dep):
	global autofiles
	global srcfiles
	global missing
	if targets.has_key(dep):
		return None
	if dep in srcfiles or dep in autofiles:
		return None
	debug("Looking for dependancy '%(dep)s'" % locals())
	# Is the dependancy matched by a rule?
	rule = rules.match(dep)
	if rule:
		( deplist, commands ) = rule
		target(dep, deplist, commands)
		debug("Found '%(dep)s' as rule => %(deplist)s" % locals())
		return deplist
	# Is the dependancy an automatic file?
	if files.copy(dep):
		# If so, add it to the automatic files list.
		debug("Found '%(dep)s' as an automatic file" % locals())
		autofiles.append(dep)
		return
	# Is the dependancy a source file?
	# If so, add it to the source files list.
	try:
		os.stat(dep)
		debug("Found '%(dep)s' as source" % locals())
		srcfiles.append(dep)
		return
	except OSError:
		print "Missing dependancy: '%s'" % dep
		missing.append(dep)

def recurse_deps(deps):
	global tree
	for dep in deps:
		moredeps = recurse_dep(dep)
		if moredeps:
			recurse_deps(moredeps)
	
def make_targets():
	( top, commands ) = rules.match(TOP)
	recurse_deps(top)

	global missing
	if missing:
		raise SystemExit, "Missing dependancies encountered, aborting."

	return ( targets, srcfiles, autofiles )
