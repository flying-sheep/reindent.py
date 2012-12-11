reindent.py
===========

The unbiased, generator-powered rewrite.


Q: Why is it better than the one coming with Python right now?
--------------------------------------------------------------

A: because the `-i` option of the command line interface allows you to indent with tabs or 2 spaces or whatever you prefer.

Q: What else? And how?
----------------------

A:

```
usage: reindent.py [-hvdnb] [-i spaces] [file [file ...]]

Reindents each input file. If none is given, code is read from stdin and
written to stdout. In this mode, all options except -i are ignored.

positional arguments:
  file                  files (and directories) to reindent

optional arguments:
  -h, --help            show this help message and exit
  -i spaces, --indentation spaces
                        indentation level depth. “0” means 1 tab
                        (default: 4 spaces)
  -v, --verbose         print information during run. can be used 2 times
                        (default: no output)
  -d, --dry-run         discard reindented file contents
                        (default: overwrite files)
  -n, --no-recurse      only reindent directly passed files
                        (default: also indent all scripts in passed directories)
  -b, --no-backup       prevent backup from being created
                        (default: create backup)
```