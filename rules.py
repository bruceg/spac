import glob
import os
import string
import sys
import types

import files
import stdexec

def join(list, sep=' '):
	return string.join(list, sep)

class Rule:
	def __init__(self, commands, depstring, makecmds,
				 stemstart, stemend):
		self.commands = commands
		self.depstring = depstring
		self.makecmds = makecmds
		self.stemstart = stemstart
		self.stemend = stemend
	def apply(self, target):
		try:
			base = target[:string.rindex(target, '.')]
		except ValueError:
			base = None
		(dirname, basename) = os.path.split(target)
		dependancies = []
		makecmds = []
		basename = os.path.basename(target)
		stem = basename[self.stemstart:self.stemend] or basename
		globls = {
			'dependon': dependancies.extend,
			'command': makecmds.append,
			'target': target,
			'base': base,
			'dir': dirname,
			'files': files,
			'basename': basename,
			'stem': stem,
			'rules': __import__('rules'),
			}
		stdexec.stdexec(self.commands, globls)
		globls['deplist_pre'] = join(dependancies)
		globls['deplist'] = join(dependancies)
		if self.depstring:
			newdep = string.split(self.depstring % locals(), ' ')
			newdep.extend(dependancies)
			dependancies = newdep
		globls['deplist'] = join(dependancies)
		if self.makecmds:
			for makecmd in self.makecmds:
				makecmds.append(makecmd % globls)
		return ( dependancies, makecmds )

targets = { }

patterns = { }

executables = [ ]

def _load_rule(path):
	base = os.path.basename(path)
	stemstart = base.find('%')
	stemend = stemstart - len(base) + 1
	lines = open(path).readlines()
	commands = ''.join(lines)
	depstring = None
	makecmds = None
	for i in range(len(lines)):
		if lines[i][:1] == ':':
			commands = ''.join(lines[:i])
			depstring = lines[i][1:].strip()
			makecmds = map(string.rstrip, lines[i+1:])
			break
	return Rule(commands, depstring, makecmds, stemstart, stemend)

def _add_rule(fullpath, entry):
	global executables
	global targets
	if not os.path.isfile(fullpath): return
	rule = _load_rule(fullpath)
	try:
		i = entry.index('%')
		patterns[(entry[:i],entry[i+1:])] = rule
	except ValueError:
		if entry[:8] == 'default=':
			executables.append(rule)
		else:
			targets[entry] = rule
	
def _scan_rules_dir(path):
	for entry in os.listdir(path):
		fullpath = os.path.join(path, entry)
		_add_rule(fullpath, entry)

def _scan_rules_ext(ext):
	for fullpath in stdexec.recglob('*.%s' % ext):
		entry = fullpath[:-len(ext)-1]
		print "Adding local rule '%s' from '%s'" % (entry, fullpath)
		_add_rule(fullpath, entry)

def load_all():
	# Scan the global rules first, then the local rules,
	# making the local rules override the globals.
	_scan_rules_dir(os.path.join(sys.path[0], 'rules'))
	try:
		_scan_rules_ext('spac')
	except OSError:
		pass

def match(target):
	rules = [ ]
	if targets.has_key(target):
		rules.append(targets[target])
	for key,rule in patterns.items():
		prestem,poststem = key
		if target[:len(prestem)] == prestem \
			   and target[-len(poststem):] == poststem:
			rules.append(rule)
	rules.extend(executables)
	for rule in rules:
		try:
			return rule.apply(target)
		except IOError:
			pass
	return None
