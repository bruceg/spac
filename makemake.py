import glob
import os
import sys

from WriteFile import WriteFile
import files
import makefile
import rules

# Global 
opt_debug = 0
ruleset = { }
missing = [ ]
srcfiles = [ ]
autofiles = [ 'Makefile', 'AUTOFILES', 'SRCFILES', 'TARGETS' ]

def split_ext(filename, div='.'):
	try:
		i = filename.rindex(div)
		return (filename[:i], filename[i+1:])
	except ValueError:
		return (filename, None)

def debug(*str):
	global opt_debug
	if opt_debug:
		print('debug:', ' '.join(str))

class Rule:
	def __init__(self, targets = None, dependancies = None, commands = None):
		self.targets = tuple(targets) or ( )
		self.dependancies = dependancies or [ ]
		self.commands = commands or [ ]

		self.add_dependancy = self.dependancies.append
		self.add_dependancies = self.dependancies.extend
		self.add_command = self.commands.append
		self.add_commands = self.commands.extend
	def __str__(self):
		return '%s: %s\n%s' % (
			' '.join(self.targets),
			' '.join(self.dependancies),
			''.join([ '\t%s\n' % line for line in self.commands ]))
	def __repr__(self):
		return "Rule(%s, %s, %s)" % (
			self.targets, self.dependancies, self.commands)

def add_rule(targets, deplist, commands):
	global ruleset
	rule = Rule(targets, deplist, commands)
	for target in targets:
		ruleset[target] = rule
	debug(repr(rule))

def recurse_dep(dep):
	global autofiles
	global srcfiles
	global missing
	if dep in ruleset:
		return None
	if dep in srcfiles or dep in autofiles:
		return None
	debug("Looking for dependancy '%(dep)s'" % locals())
	# Is the dependancy matched by a rule?
	rule = rules.match(dep)
	if rule:
		( targets, deplist, commands ) = rule
		add_rule(targets, deplist, commands)
		debug("Found '%(dep)s' as rule %(targets)s => %(deplist)s" % locals())
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
		print("Missing dependancy: '%s'" % dep)
		missing.append(dep)

def recurse_deps(deps):
	global tree
	for dep in deps:
		moredeps = recurse_dep(dep)
		if moredeps:
			recurse_deps(moredeps)
	
def make_ruleset():
	( targets, default_deps, default_commands ) = rules.match('DEFAULT')
	recurse_deps(default_deps)
	( targets, top, commands ) = rules.match('TOP')
	recurse_deps(top)

	global missing
	if missing:
		raise SystemExit("Missing dependancies encountered, aborting.")

	targets = list(ruleset.keys())
	ruleset['DEFAULT'] = Rule(('DEFAULT',), default_deps, default_commands)
	rruleset = dict([ (rule.targets,rule) for rule in list(ruleset.values()) ])
	return ( rruleset, targets, srcfiles, autofiles )
