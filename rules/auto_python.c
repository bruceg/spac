:
( set -e; PATH="/bin:/usr/bin:/usr/local/bin:$$PATH"; export PATH; \
  python=`which python`; \
  echo 'const char auto_python[] = "'$$python'";' ) >auto_python.c
