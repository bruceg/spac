: conf-%(stem)s
head -n 1 conf-%(stem)s | \
  sed -e 's/"/\\"/g' \
      -e 's/^/const char conf_%(stem)s[] = "/' \
      -e 's/$$/";/' >conf_%(stem)s.c
