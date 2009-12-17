import glob
import os
import sys

from WriteFile import WriteFile

header = """\
# Don't edit Makefile!  Use conf-* for configuration.
#
# Generated by spac see http://untroubled.org/spac/

SHELL=/bin/sh

DEFAULT: all

"""

def write(ruleset, filename='Makefile'):
	names = ruleset.keys()
	names.sort()
	
	makefile = WriteFile('Makefile')
	makefile.write(header)
	#makefile.write("everything: %s\n\n" % ' '.join(names))
	
	for name in names:
		makefile.write(str(ruleset[name]))
		makefile.write('\n')
	makefile.close()
