#!/usr/bin/env python3

from unittest import TestCase, main
from reindent import Reindenter, parser

class TestCmdLineRun(TestCase):
	def testReindenter(self):
		with open('test_before.py') as before, open('test_after.py') as after:
			indenter = Reindenter(before)
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

if __name__ == '__main__':
	main()