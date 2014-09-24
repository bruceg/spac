import glob
import os
import sys

from WriteFile import WriteFile
import stdexec

FILES = sys.intern('FILES')

loaded_rules = { }

recurse_skip = [
	'CVS',
	'.svn',
	]

def recurse_dir(dir):
	list = [ ]
	for file in os.listdir(dir or '.'):
		if file[-1:] == '~': continue
		if file in recurse_skip: continue
		fullpath = os.path.join(dir, file)
		if os.path.isfile(fullpath):
			list.append(fullpath)
		elif os.path.isdir(fullpath):
			list.extend(recurse_dir(fullpath))
	return list

class FileList:
	def __init__(self):
		self.filelist = { }
	def add_one(self, filename, content=None):
		#if self.filelist.has_key(filename):
		#	raise ValueError, "File '%s' already in list." % filename
		if content is None:
			try:
				content = open(filename).read()
			except IOError:
				raise SystemExit("Missing file: '%s'" % filename)
		self.filelist[filename] = content
	def add_list(self, list):
		for item in list:
			self.add_one(item, None)
	def add_dir(self, dir):
		for item in recurse_dir(dir):
			self.add_one(item, None)
	def del_one(self, filename):
		if filename in self.filelist:
			del self.filelist[filename]
	def del_list(self, list):
		for item in list:
			self.del_one(item)
	def merge_list(self, list):
		for item in list:
			if item not in self.filelist:
				self.filelist[item] = None
	def keys(self):
		return sorted(list(self.filelist.keys()))
	def __getitem__(self, key): return self.filelist[key]
	def __setitem__(self, key, value): self.filelist[key] = value

def load_file(fullpath, base, globls):
	global loaded_rules
	if base in loaded_rules:
		return
	loaded_rules[base] = 1
	print("Loading dist rules from '%s'" % fullpath)
	return stdexec.stdexecfile(fullpath, globls)

def load_dir(path, globls):
	for file in os.listdir(path):
		if file in recurse_skip: continue
		load_file(os.path.join(path, file), file, globls)

def load_ext(ext, globls):
	global loaded_rules
	for file in glob.glob('*.%s' % ext):
		load_file(file, file[:-len(ext)-1], globls)

def build_files(package, version):
	files = FileList()
	files.add_one(FILES, '')
	globls = {
		'dir': files.add_dir,
		'file': files.add_one,
		'files': files.add_list,
		'nofile': files.del_one,
		'nofiles': files.del_list,
		'package': package,
		'version': version,
		}
	try:
		load_ext('dist', globls)
	except OSError:
		pass
	load_dir(os.path.join(sys.path[0], 'dist'), globls)
	return files

def copyfile(filename, contents, directory):
	filename = os.path.join(directory, filename)
	(dir,ign) = os.path.split(filename)
	try:
		os.makedirs(dir, 0o755)
	except OSError:
		pass
	out = open(filename, 'w')
	out.write(contents)
	out.close()

def main(package, version):
	files = build_files(package, version)

	filelist = list(files.keys())
	files[FILES] = '\n'.join(filelist) + '\n'
	
	base = package + "-" + version
	os.mkdir(base, 0o777)
	for file in filelist:
		copyfile(file, files[file], base)

	print("Writing tarball '%s.tar.gz'" % base)
	try: os.unlink('%s.tar.gz' % base)
	except OSError: pass
	os.system('tar -cf - %s | gzip -9 >%s.tar.gz' % (base, base))

	print("Cleaning up")
	os.system('rm -rf %s' % base)

	os.system('md5sum %s.tar.gz' % base)
	try: os.unlink(base + '.tar.gz.sig')
	except OSError: pass
	os.system('gpg --detach-sign --armor --output %s.tar.gz.sig %s.tar.gz' % (
		base, base))
