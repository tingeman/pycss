from __future__ import absolute_import
import unittest
import os
import os.path
import sys
from matplotlib.pyplot import savefig
from matplotlib import pyplot
import numpy as np

import pycss
import pdb


"""
Available assertion methods, callable within TestCase by invoking f.ex.:

self.assertRaises(func(), ValueError)

or

with self.assertRaises(ValueError):
    some_method_or_function_call(*args, **kwargs)

List of available assertions:
-----------------------------
unittest.TestCase.assertAlmostEqual            
unittest.TestCase.assertAlmostEquals           
unittest.TestCase.assertDictContainsSubset     
unittest.TestCase.assertDictEqual              
unittest.TestCase.assertEqual                  
unittest.TestCase.assertEquals                 
unittest.TestCase.assertFalse                  
unittest.TestCase.assertGreater                
unittest.TestCase.assertGreaterEqual           
unittest.TestCase.assertIn                 
unittest.TestCase.assertIs                 
unittest.TestCase.assertIsInstance         
unittest.TestCase.assertIsNone         
unittest.TestCase.assertIsNot          
unittest.TestCase.assertIsNotNone      
unittest.TestCase.assertItemsEqual     
unittest.TestCase.assertLess           
unittest.TestCase.assertLessEqual      
unittest.TestCase.assertListEqual      
unittest.TestCase.assertMultiLineEqual 
unittest.TestCase.assertNotAlmostEqual 
unittest.TestCase.assertNotAlmostEquals
unittest.TestCase.assertNotEqual
unittest.TestCase.assertNotEquals
unittest.TestCase.assertNotIn
unittest.TestCase.assertNotIsInstance
unittest.TestCase.assertNotRegexpMatches
unittest.TestCase.assertRaises
unittest.TestCase.assertRaisesRegexp
unittest.TestCase.assertRegexpMatches
unittest.TestCase.assertSequenceEqual
unittest.TestCase.assertSetEqual
unittest.TestCase.assertTrue
unittest.TestCase.assertTupleEqual
""" 

# -----------------------------------------------------------------------------
# Module initialization code
# -----------------------------------------------------------------------------

def module_path():
    """Return the path of the current module (filename is stripped away)"""
    def ensure_unicode(s):
        """ensure that string is unicode"""
        if not isinstance(s, unicode):
            encoding = sys.getfilesystemencoding()
            s = unicode(s, encoding)
        return s
            
    def we_are_frozen():
        # All of the modules are built-in to the interpreter, e.g., by py2exe
        return hasattr(sys, "frozen")
    
    if we_are_frozen():
        return os.path.dirname(ensure_unicode(sys.executable))
        
    return os.path.dirname(ensure_unicode(__file__))

    
# To make test suite callable from within ipython
# http://stackoverflow.com/questions/11536764/attempted-relative-import-in-non-package-even-with-init-py
if __name__ == '__main__' and __package__ is None:
    sys.path.append(os.path.dirname(os.path.abspath('.')))


# -----------------------------------------------------------------------------
# Setup and Teardown functions on module level
# -----------------------------------------------------------------------------

def setUpModule(*args, **kwargs):
    pass
    
def tearDownModule(*args, **kwargs):
    pass
    

# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------


def part_sum(start=None, end=None):
    """Calculates partial sum"""
    sum = 0
    for x in xrange(start, end):
        if x % 2 == 0:
           sum -= 1.0 / x
        else:
           sum += 1.0 / x
    return sum


def wrapper(listarg=None):
    # just allowing list input to part_sum
    return part_sum(*listarg)


def squares(start=None, end=None):
    """Calculates partial sum"""
    squares = np.zeros((4))
    temp = (np.arange(start,end)**2)
    squares[0:min(len(temp),4)] = temp[-min(len(temp),4):]
    return squares


class TemplateTestCase(unittest.TestCase):
    """Tests for some new module or class etc."""
    
    def setUp(self):
        self.backend = pyplot.get_backend()
        pyplot.switch_backend('agg')

    def tearDown(self):
        pyplot.switch_backend(self.backend)
    
    def test_basic_cssengine_usage(self):
        """test CSSEngine usage"""
        arguments =  dict(start=1, end=10000)
        opt_params = arguments.keys()
        css_engine = pycss.CSSEngine(part_sum, opt_params, arguments, 2)
        #css_engine.locals = locals()
        css_engine.globals = globals()
        css_engine.do_computations()

        self.assertIsNotNone(css_engine.basic_result)
        self.assertAlmostEqual(css_engine.basic_result, part_sum(1,10000))
        self.assertIn('start', css_engine.results)
        self.assertAlmostEqual(css_engine.results['start'], part_sum(2,10000))
        self.assertIn('end', css_engine.results)
        self.assertAlmostEqual(css_engine.results['end'], part_sum(1,20000))

        css_engine.calculate_css()
        fig = css_engine.plot_css()
        fig.savefig(os.path.join(module_path(), 'basic_css_test.png'), format='png')
        
    def test_cssengine_list_argument(self):
        """test CSSEngine usage"""
        arguments =  dict(listarg=[1,10000])
        opt_params = ['listarg[0]','listarg[1]']
        css_engine = pycss.CSSEngine(wrapper, opt_params, arguments, 2)
        #css_engine.locals = locals()
        css_engine.globals = globals()
        css_engine.do_computations()

        self.assertIsNotNone(css_engine.basic_result)
        self.assertAlmostEqual(css_engine.basic_result, part_sum(1,10000))
        self.assertIn('listarg[0]', css_engine.results)
        self.assertAlmostEqual(css_engine.results['listarg[0]'], part_sum(2,10000))
        self.assertIn('listarg[1]', css_engine.results)
        self.assertAlmostEqual(css_engine.results['listarg[1]'], part_sum(1,20000))

        css_engine.calculate_css()
        fig = css_engine.plot_css()
        fig.savefig(os.path.join(module_path(), 'listarg_css_test.png'), format='png')


    def test_cssengine_array_out(self):
        """test CSSEngine usage"""
        arguments =  dict(start=1, end=6)
        opt_params = ['start', 'end']
        css_engine = pycss.CSSEngine(squares, opt_params, arguments, 2)
        #css_engine.locals = locals()
        css_engine.globals = globals()
        css_engine.do_computations()

        self.assertIsNotNone(css_engine.basic_result)
        self.assertItemsEqual(css_engine.basic_result, squares(1,6))
        self.assertIn('start', css_engine.results)
        self.assertItemsEqual(css_engine.results['start'], squares(2,6))
        self.assertIn('end', css_engine.results)
        self.assertItemsEqual(css_engine.results['end'], squares(1,12))

        css_engine.calculate_css()
        fig = css_engine.plot_css()
        fig.savefig(os.path.join(module_path(), 'arrayout_css_test.png'), format='png')

# -----------------------------------------------------------------------------
# Running the tests
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
