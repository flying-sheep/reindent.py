#!/usr/bin/env python3

"""
Reindents each input file. If none is given,
code is read from stdin and written to stdout.
In this mode, all options except -i are ignored.
"""

#TODO: don’t change multiline strings that aren’t docstrings

__version__ = '1'

import os, sys, logging
from io import StringIO
from shutil import copyfile
from argparse import ArgumentParser
from collections import defaultdict
from tokenize import tokenize, detect_encoding

def indentation(i):
	try:
		i = int(i)
		if i == 0:
			return '\t'
		else:
			return ' ' * i
	except ValueError:
		return i

parser = ArgumentParser(description=__doc__)

parser.add_argument('files', metavar='file', nargs='*',
	help='files (and directories) to reindent')
parser.add_argument('-i', '--indentation', metavar='spaces', type=indentation, default='4',
	help='indentation level depth. “0” means 1 tab (default: 4 spaces)')
parser.add_argument('-v', '--verbose', action='count', default=0,
	help='print information during run. can be used 2 times (default: no output)')
parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
	help='discard reindented file contents (default: overwrite files)')
parser.add_argument('-n', '--no-recurse', dest='recurse', action='store_false',
	help='only reindent directly passed files (default: also indent all scripts in passed directories)')
parser.add_argument('-b', '--no-backup', dest='backup', action='store_false',
	help='prevent backup from being created (default: create backup)')

LOG_LEVELS = [
	logging.WARNING,
	logging.INFO,
	logging.DEBUG,
]

def main(args):
	options = parser.parse_args(args)
	logging.basicConfig(format='⇒ %(message)s', level=LOG_LEVELS[min(options.verbose, 2)])
	
	for file in options.files:
		check(file, options)
	if not options.files:
		indenter = Reindenter(sys.stdin, options.indentation)
		indenter()
		indenter.write(sys.stdout)

def checkall(directory, options):
	"""
	runs check on all files in directory,
	provided they aren’t hidden or in a hidden subdirectory
	"""
	for dirpath, dirnames, filenames in os.walk(directory):
		accept = [dirn for dirn in dirnames if not dirn.startswith('.')]
		dirnames[:] = accept
		for filename in filenames:
			if not filename.startswith('.'):
				fullname = os.path.join(dirpath, filename)
				check(fullname, options)

def check(file, options=parser.parse_args([])):
	"""Reindents a input file or all files in a input directory"""
	if os.path.isdir(file) and not os.path.islink(file):
		logging.info('%s is a directory,', file)
		if options.recurse:
			logging.info('listing…')
			checkall(file, options)
			return
		else:
			logging.info('but we do not recurse.')
	
	logging.info('checking %s…', file)
	with open(file, 'rb') as f:
		encoding, _ = detect_encoding(f.readline)
	try:
		with open(file, encoding=encoding) as f:
			indenter = Reindenter(f, options.indentation)
	except IOError as msg:
		print('{}: I/O Error: {}'.format(file, msg), file=sys.stderr)
		return
	
	if indenter():
		logging.info('changed.')
		if options.dry_run:
			logging.info('But this is a dry run, so leaving it alone.')
		else:
			if options.backup:
				bak = file + '.bak'
				# do not overwrite another backup file
				if os.path.exists(bak):
					n = 1
					bak += str(n)
					while os.path.exists(bak):
						bak = '{}{}'.format(bak[:-1], n)
						n += 1
					
				copyfile(file, bak)
				logging.info('backed up %s to %s.', file, bak)
			with open(file, 'w', encoding=encoding) as f:
				indenter.write(f)
			logging.info('wrote new %s.', file)
		return True
	else:
		logging.info('unchanged.')
		return False

def reindent(string, indentation='    '):
	reindenter = Reindenter(StringIO(string), indentation)
	reindenter()
	return ''.join(reindenter.after)

class Reindenter:
	def __init__(self, f, indentation='    '):
		self.indentation = indentation
		self.before = f.readlines()
		self.lines = [line.rstrip().expandtabs() for line in self.before]
		self.after = []
	
	def __call__(self):
		"""
		Fills self.after with the reindented version of self.before.
		Returns then True if self.after is different from self.before.
		"""
		lines = iter(line.encode() + b'\n' for line in self.lines)
		stats = self.parse_tokens(tokenize(lines.__next__))
		
		last_stat_on = 0
		
		for lineno, stat, nlines in stats:
			stat = stat or [] #we could process comments specially here
			for l in range(last_stat_on, lineno+nlines):
				line = self.lines[l]
				line = line[sum(len(s) for s in stat):]
				line = (len(stat) * self.indentation) + line #TODO
				if not l == len(self.lines) - 1:
					line += '\n'
				self.after.append(line)
				
				sym = '×' if l == lineno - 1 else ' '
				logging.debug("{}{:3} {!r:31} |{}".format(sym, l, stat, line))
			
			last_stat_on = l+1
		
		return self.before != self.after
	
	def write(self, f):
		"""
		Writes the reindented self.after to file f.
		"""
		f.writelines(self.after)
	
	def parse_tokens(self, tokens):
		"""
		Traverses the tokens and yields (linenumber, indentation) tuples.
		Those contain a list of the indentation levels of the line, e.g.
		(5, ['\t', '        ']) for a twice (badly) indented line #6.
		"""
		from tokenize import INDENT, DEDENT, NEWLINE, COMMENT, NL, ENDMARKER, ENCODING
		
		find_stmt = True
		level = []
		
		for typ, token, (lineno, col), end, line in tokens:
			lineno -= 1
			if typ == NEWLINE:
				# A program statement, or ENDMARKER, will eventually follow,
				# after some (possibly empty) run of tokens of the form
				#     (NL | COMMENT)* (INDENT | DEDENT+)?
				find_stmt = True
			
			elif typ == INDENT:
				find_stmt = True
				level.append(token)
			
			elif typ == DEDENT:
				find_stmt = True
				level.pop()
			
			elif typ == COMMENT:
				if find_stmt:
					yield (lineno, None, line.count('\n'))
					# but we're still looking for a new stmt, so leave
					# find_stmt alone
			
			elif typ in (NL, ENDMARKER, ENCODING):
				pass
			
			elif find_stmt:
				# This is the first 'real token' following a NEWLINE, so it
				# must be the first token of the next program statement, or an
				# ENDMARKER.
				find_stmt = False
				cumul_indent = [len(l) for l in level]
				indent = []
				for i in reversed(range(len(cumul_indent))):
					full = cumul_indent[i]
					prefix = cumul_indent[i - 1] if i > 0 else 0
					indent.insert(0, ' ' * (full - prefix))
				yield (lineno, indent, line.count('\n'))

if __name__ == '__main__':
	main(sys.argv[1:])
