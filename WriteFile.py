import os

class WriteFile:
	def __init__(self, filename, tmpext = '.tmp'):
		self.filename = filename
		self.tmpfile = filename + tmpext
		self.out = open(self.tmpfile, 'w')
		self.ok = 1
	def close(self):
		self.out.close()
		print "Writing '%s'" % self.filename
		import os
		os.rename(self.tmpfile, self.filename)
		self.tmpfile = None
		self.filename = None
	def __del__(self):
		if self.tmpfile:
			print "Removing temporary file '%s'" % self.tmpfile
			os.unlink(self.tmpfile)
	def writelist(self, list):
		list = list[:]
		list.sort()
		for item in list:
			self.write('%s\n' % item)
		return self
	def write(self, data):
		try:
			self.out.write(data)
		except IOError, msg:
			self.ok = 0
			raise IOError, msg
		return self
	def writelines(self, data):
		try:
			self.out.writelines(data)
		except IOError, msg:
			self.ok = 0
			raise IOError, msg
		return self
