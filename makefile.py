import glob
import os
import string
import sys

from WriteFile import WriteFile

header = """\
# Don't edit Makefile!  Use conf-* for configuration.
#
# Generated by spac see http://untroubled.org/spac/

SHELL=/bin/sh

DEFAULT: all

"""

def write(targets, filename='Makefile'):
	names = targets.keys()
	names.sort()
	
	makefile = WriteFile('Makefile')
	makefile.write(header)
 	#makefile.write("everything: %s\n\n" % string.join(names, ' '))
	
	for name in names:
		makefile.write(str(targets[name]))
		makefile.write('\n')
	makefile.close()
