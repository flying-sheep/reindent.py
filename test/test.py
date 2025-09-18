#!/usr/bin/env python3

from unittest import TestCase, main
from reindent import Reindenter, reindent, parser

class TestCmdLineRun(TestCase):
	maxDiff = None
	def testReindenter(self):
		with open('test_before.py') as before, open('test_after.py') as after:
			indenter = Reindenter(before, '\t')
			expected = after.readlines()
		
		self.assertTrue(indenter())
		self.assertEqual(indenter.after, expected)

class TestParser(TestCase):
	def testIndentation(self):
		opts = parser.parse_args([])
		self.assertEqual(opts.indentation, ' ' * 4)
		
		opts = parser.parse_args(['-i', '0'])
		self.assertEqual(opts.indentation, '\t')
		
		opts = parser.parse_args(['-i', '2'])
		self.assertEqual(opts.indentation, '  ')
		
		opts = parser.parse_args(['-i', '\t'])
		self.assertEqual(opts.indentation, '\t')

def _simpleTest(before, after):
	def method(self):
		self.assertEqual(reindent(before), after)
	return method

class TestConversions(TestCase):
	def testReindent(self):
		self.assertEqual(reindent(''), '')
	
	def testHangingComment(self):
		hangingComment = '''
def bla(): #a
           #b
'''
		self.assertEqual(reindent(hangingComment + ' pass'), hangingComment + '    pass')

	def testMultiLineString(self):
		src = '''"""Top multiline string
second line
  Third and last line"""

a=1

"""  First line  \t
   second line
\t\tthird line  
  """\
'''
		expected = '''"""Top multiline string
second line
  Third and last line"""

a=1

"""  First line
   second line
                third line
  """\
'''
		self.assertEqual(reindent(src), expected)

if __name__ == '__main__':
	print(TestConversions().testReindent())
	main(verbosity=2)