import unittest

from tclwrapper import tclutil

class TestTCLUtil(unittest.TestCase):
    tclstring_repr = 'a b {c {d e} f} {g h}'
    list_repr = ['a', 'b', ['c', ['d', 'e'], 'f'], ['g', 'h']]
    tuple_repr = ('a', 'b', ('c', ('d', 'e'), 'f'), ('g', 'h'))
    flat_list_repr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    def test_tclstring_to_nested_list(self):
        def check_tclstring_to_nested_list(tclstring, nestedlist):
            x = tclutil.tclstring_to_nested_list(tclstring)
            self.assertEqual(x, nestedlist)

        check_tclstring_to_nested_list( '' , () )
        check_tclstring_to_nested_list( 'a' , ('a',) )
        check_tclstring_to_nested_list( 'a b' , ('a', 'b') )
        check_tclstring_to_nested_list( 'a b c' , ('a', 'b', 'c') )
        check_tclstring_to_nested_list( 'abc' , ('abc',) )
        check_tclstring_to_nested_list( '{a b} c' , (('a', 'b'), 'c') )
        check_tclstring_to_nested_list( '{a {b c}} d' , (('a', ('b', 'c')), 'd') )

        # TODO: make this work
        # check_tclstring_to_nested_list( '{{{a} {b}}} c' , (('{a} {b}', 'c') )

    def test_tclstring_to_nested_list_with_levels(self):
        def check_tclstring_to_nested_list_with_levels(levels, tclstring, nestedlist):
            x = tclutil.tclstring_to_nested_list(tclstring, levels = levels)
            self.assertEqual(x, nestedlist)

        check_tclstring_to_nested_list_with_levels( 0, 'a b c  d', 'a b c  d' )
        check_tclstring_to_nested_list_with_levels( 1, 'a b c  d', ('a', 'b', 'c', 'd') )
        check_tclstring_to_nested_list_with_levels( 2, 'a b c  d', (('a',), ('b',), ('c',), ('d',)) )
        check_tclstring_to_nested_list_with_levels( 3, 'a b c  d', ((('a',),), (('b',),), (('c',),), (('d',),)) )
        check_tclstring_to_nested_list_with_levels( 0, '{a b} {c d} {e f} {g h}', '{a b} {c d} {e f} {g h}' )
        check_tclstring_to_nested_list_with_levels( 1, '{a b} {c d} {e f} {g h}', ('a b','c d','e f','g h') )
        check_tclstring_to_nested_list_with_levels( 2, '{a b} {c d} {e f} {g h}', (('a','b'),('c','d'),('e','f'),('g','h')) )
        check_tclstring_to_nested_list_with_levels( 0, '{a {b c}} d', '{a {b c}} d' )
        check_tclstring_to_nested_list_with_levels( 1, '{a {b c}} d', ('a {b c}','d') )
        check_tclstring_to_nested_list_with_levels( 2, '{a {b c}} d', (('a','b c'),('d',)) )

    def test_nested_list_to_tclstring(self):
        # This function works on nested lists and nested tuples
        x = tclutil.nested_list_to_tclstring(TestTCLUtil.list_repr)
        self.assertEqual(x, TestTCLUtil.tclstring_repr)
        y = tclutil.nested_list_to_tclstring(TestTCLUtil.tuple_repr)
        self.assertEqual(y, TestTCLUtil.tclstring_repr)

    def test_tclstring_to_flat_list(self):
        # This function should flatten the resulting list
        x = tclutil.tclstring_to_flat_list(TestTCLUtil.tclstring_repr)
        self.assertEqual(x, TestTCLUtil.flat_list_repr)
