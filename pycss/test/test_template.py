import unittest
import os
import os.path
import sys
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
    
class TemplateTestCase(unittest.TestCase):
    """Tests for some new module or class etc."""
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_module_function_or_class_method(self):
        """What is tested here?"""
        self.assertTrue(True)
        
        
# -----------------------------------------------------------------------------
# Running the tests
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
