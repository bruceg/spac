conffile = 'conf-' + stem.replace('_', '-')
dependon([conffile])
:
head -n 1 %(conffile)s | \
  sed -e 's/"/\\"/g' \
      -e 's/^/const char conf_%(stem)s[] = "/' \
      -e 's/$$/";/' >conf_%(stem)s.c
