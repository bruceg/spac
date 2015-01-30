: VERSION
echo 'const char auto_version[] = "'$$( head -n 1 VERSION )'";' > auto_version.c
