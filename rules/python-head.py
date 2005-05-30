:
( set -e; PATH="/bin:/usr/bin:/usr/local/bin:$$PATH"; export PATH; \
  python=`which python`; \
  echo "#! $$python"; \
  echo "# WARNING: This file was auto-generated. Do not edit!" ) >python-head.py
