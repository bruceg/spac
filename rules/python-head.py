:
( set -e; PATH="/bin:/usr/bin:/usr/local/bin:$$PATH"; export PATH; \
  python=`which python2 || which python 2>/dev/null`; \
  echo "#! $$python"; \
  echo "# WARNING: This file was auto-generated. Do not edit!" ) >python-head.py
