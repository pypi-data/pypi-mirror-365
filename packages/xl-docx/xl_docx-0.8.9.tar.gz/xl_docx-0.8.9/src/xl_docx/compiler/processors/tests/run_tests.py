#!/usr/bin/env python3
"""
Simple test runner for xl_docx processors
"""
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_basic_tests():
    """Run basic tests to verify the test suite is working"""
    print("=== xl_docx Processors Test Suite ===")
    print()
    
    # Test imports
    try:
        from xl_docx.compiler.processors.base import BaseProcessor
        from xl_docx.compiler.processors.style import StyleProcessor
        from xl_docx.compiler.processors.directive import DirectiveProcessor
        from xl_docx.compiler.processors.paragraph import ParagraphProcessor
        from xl_docx.compiler.processors.pager import PagerProcessor
        from xl_docx.compiler.processors.table import TableProcessor
        print("✓ All processors imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test basic functionality
    try:
        # Test BaseProcessor
        params = {'a': 1, 'b': 2}
        a, b = BaseProcessor.retrieve(params, ['a', 'b'])
        assert a == 1 and b == 2
        print("✓ BaseProcessor.retrieve() works")
        
        # Test StyleProcessor
        processor = StyleProcessor()
        assert processor.styles == {}
        print("✓ StyleProcessor initialization works")
        
        # Test DirectiveProcessor
        xml = '<div v-if="condition">content</div>'
        result = DirectiveProcessor._process_v_if(xml)
        assert '{% if condition %}' in result
        print("✓ DirectiveProcessor._process_v_if() works")
        
        # Test ParagraphProcessor
        xml = '<xl-p>content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:p>' in result
        print("✓ ParagraphProcessor.compile() works")
        
        # Test PagerProcessor
        processor = PagerProcessor()
        xml = '<xl-pager />'
        result = processor.compile(xml)
        assert '<w:sdt>' in result
        print("✓ PagerProcessor.compile() works")
        
        # Test TableProcessor
        xml = '<xl-table><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tbl>' in result
        print("✓ TableProcessor.compile() works")
        
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False
    
    print()
    print("=== Test Summary ===")
    print("✓ All basic functionality tests passed")
    print()
    print("To run the full test suite with pytest:")
    print("  pytest -v")
    print()
    print("To run specific test files:")
    print("  pytest test_base.py -v")
    print("  pytest test_style.py -v")
    print("  pytest test_directive.py -v")
    print("  pytest test_paragraph.py -v")
    print("  pytest test_pager.py -v")
    print("  pytest test_table.py -v")
    
    return True

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1) 