:
( set -e; PATH="/bin:/usr/bin:/usr/local/bin:$$PATH"; export PATH; \
  python2=`which python2`; \
  echo 'const char auto_python2[] = "'$$python2'";' ) >auto_python2.c
