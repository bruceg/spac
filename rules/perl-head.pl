:
( set -e; PATH="/bin:/usr/bin:/usr/local/bin:$$PATH"; export PATH; \
  perl=`which perl`; \
  echo "#! $$perl"; \
  echo "# WARNING: This file was auto-generated. Do not edit!"; \
  echo ) >perl-head.pl
