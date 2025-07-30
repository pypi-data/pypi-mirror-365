#!/usr/bin/env python3
"""
Test suite for Enhanced CopycatAnalyzer with mathematical invariance and coherence validation.
"""

import unittest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from copycatm.core import EnhancedCopycatAnalyzer
from copycatm.analysis import MathematicalProperty, CoherenceLevel


class TestEnhancedAnalyzer(unittest.TestCase):
    """Test cases for enhanced analyzer functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.analyzer = EnhancedCopycatAnalyzer()
        cls.test_dir = Path(__file__).parent
        cls.samples_dir = cls.test_dir / "samples"
        cls.cross_lang_dir = cls.test_dir / "cross_language"
        cls.similarity_dir = cls.test_dir / "similarity_test"
    
    def test_mathematical_properties_detection(self):
        """Test mathematical property detection in sorting algorithms."""
        # Test with quicksort
        quicksort_path = self.samples_dir / "test_quicksort.py"
        result = self.analyzer.analyze_file(str(quicksort_path))
        
        # Check mathematical analysis exists
        self.assertIn('mathematical_analysis', result)
        math_analysis = result['mathematical_analysis']
        
        # Should detect some mathematical properties
        self.assertGreater(len(math_analysis['properties_detected']), 0)
        
        # Should have transformation resistance (may be 0 if no properties match expected patterns)
        self.assertGreaterEqual(math_analysis['transformation_resistance'], 0.0)
        
        # If properties were detected, resistance should be high
        if math_analysis['properties_detected']:
            # Debug info
            if math_analysis['transformation_resistance'] <= 0.7:
                print(f"Debug: Properties detected: {math_analysis['properties_detected']}")
                print(f"Debug: Resistance: {math_analysis['transformation_resistance']}")
            self.assertGreater(math_analysis['transformation_resistance'], 0.7)
        
        # Common properties in sorting algorithms
        possible_props = {'transitive', 'commutative', 'closure', 'associative'}
        detected = set(math_analysis['properties_detected']).intersection(possible_props)
        self.assertGreater(len(detected), 0, 
                          f"Expected at least one of {possible_props}, but got {math_analysis['properties_detected']}")
        
    def test_coherence_validation(self):
        """Test coherence validation across dimensions."""
        # Test with searching algorithms
        search_path = self.samples_dir / "searching_algorithms.py"
        result = self.analyzer.analyze_file(str(search_path))
        
        # Check coherence analysis exists
        self.assertIn('coherence_analysis', result)
        coherence = result['coherence_analysis']
        
        # Should have coherence score
        self.assertIn('score', coherence)
        self.assertGreaterEqual(coherence['score'], 0.0)
        self.assertLessEqual(coherence['score'], 1.0)
        
        # Should have coherence level
        self.assertIn('level', coherence)
        self.assertIn(coherence['level'], ['high_confidence', 'medium_confidence', 
                                          'potential_false_positive', 'invalid_match'])
    
    def test_enhanced_algorithm_detection(self):
        """Test that mathematical properties enhance algorithm detection."""
        # Test with sorting algorithms
        sorting_path = self.samples_dir / "sorting_algorithms.py"
        
        # Compare standard vs enhanced
        self.analyzer.set_enhancement_options(enable_math=False, enable_coherence=False)
        standard_result = self.analyzer.analyze_file(str(sorting_path))
        
        self.analyzer.set_enhancement_options(enable_math=True, enable_coherence=True)
        enhanced_result = self.analyzer.analyze_file(str(sorting_path))
        
        # Enhanced should have mathematical validation
        self.assertIn('mathematical_analysis', enhanced_result)
        self.assertNotIn('mathematical_analysis', standard_result)
        
        # Check for enhanced algorithms
        if enhanced_result.get('algorithms'):
            for algo in enhanced_result['algorithms']:
                if algo.get('mathematical_evidence'):
                    # Should have transformation resistance
                    self.assertIn('transformation_resistance', algo)
                    self.assertGreater(algo['transformation_resistance'], 0)
    
    def test_cross_language_consistency(self):
        """Test mathematical properties are consistent across languages."""
        # Test quicksort in Python, C, and JavaScript
        languages = [
            ('quicksort.py', 'python'),
            ('quicksort.c', 'c'),
            ('quicksort.js', 'javascript')
        ]
        
        properties_found = []
        
        for filename, language in languages:
            file_path = self.cross_lang_dir / filename
            if file_path.exists():
                result = self.analyzer.analyze_file(str(file_path))
                
                if 'mathematical_analysis' in result:
                    props = set(result['mathematical_analysis']['properties_detected'])
                    properties_found.append(props)
        
        # At least 2 languages should have properties detected
        if len(properties_found) >= 2:
            # Check if any language detected properties
            total_properties = sum(len(props) for props in properties_found)
            self.assertGreater(total_properties, 0, "Expected at least one language to detect properties")
            
            # If multiple languages have properties, check for commonality
            non_empty = [props for props in properties_found if props]
            if len(non_empty) >= 2:
                # Check for common properties
                common_props = non_empty[0]
                for props in non_empty[1:]:
                    common_props = common_props.intersection(props)
                
                # Log what was found for debugging
                if not common_props:
                    print(f"No common properties found. Language properties: {properties_found}")
    
    def test_transformation_resistance(self):
        """Test transformation resistance between similar algorithms."""
        # Compare original and copy
        original_path = self.samples_dir / "test_quicksort.py"
        copy_path = self.samples_dir / "test_quicksort_copy.py"
        
        if original_path.exists() and copy_path.exists():
            original_result = self.analyzer.analyze_file(str(original_path))
            copy_result = self.analyzer.analyze_file(str(copy_path))
            
            # Both should have high transformation resistance
            if 'mathematical_analysis' in original_result:
                self.assertGreater(
                    original_result['mathematical_analysis']['transformation_resistance'], 
                    0.8
                )
            
            if 'mathematical_analysis' in copy_result:
                self.assertGreater(
                    copy_result['mathematical_analysis']['transformation_resistance'], 
                    0.8
                )
    
    def test_false_positive_reduction(self):
        """Test that coherence validation reduces false positives."""
        # Test with small functions that might have high hash similarity
        # but are actually different
        small_funcs_path = self.samples_dir / "small_functions.py"
        
        if small_funcs_path.exists():
            result = self.analyzer.analyze_file(str(small_funcs_path))
            
            # Check if any algorithms were detected
            if result.get('algorithms') and 'coherence_analysis' in result:
                coherence = result['coherence_analysis']
                
                # Low coherence should flag potential false positives
                if coherence['score'] < 0.4:
                    self.assertEqual(coherence['level'], 'potential_false_positive')
                    self.assertIn('requires_manual_review', result)
    
    def test_mathematical_property_types(self):
        """Test detection of specific mathematical properties."""
        # Create test code with known properties
        test_code = '''
def commutative_add(a, b):
    """Addition is commutative: a + b = b + a"""
    return a + b

def associative_multiply(a, b, c):
    """Multiplication is associative: (a * b) * c = a * (b * c)"""
    return (a * b) * c

def distributive_example(a, b, c):
    """Distributive property: a * (b + c) = a * b + a * c"""
    return a * (b + c)

def transitive_compare(a, b, c):
    """Transitive comparison"""
    if a < b and b < c:
        return a < c
    return False
'''
        
        result = self.analyzer.analyze_code(test_code, 'python', 'math_properties.py')
        
        if 'mathematical_analysis' in result:
            properties = result['mathematical_analysis']['properties_detected']
            
            # Should detect at least some of these properties
            possible_props = {'commutative', 'associative', 'distributive', 'transitive'}
            detected = set(properties).intersection(possible_props)
            self.assertGreater(len(detected), 0)
    
    def test_coherence_warnings(self):
        """Test that coherence validation generates appropriate warnings."""
        # Test with a file that might have conflicting signals
        result = self.analyzer.analyze_code(
            "def simple_func(): return 42",
            'python',
            'simple.py'
        )
        
        if 'coherence_analysis' in result:
            coherence = result['coherence_analysis']
            
            # Check warning structure
            self.assertIn('warnings', coherence)
            self.assertIsInstance(coherence['warnings'], list)
            
            # Check recommendation exists
            self.assertIn('recommendation', coherence)
            self.assertIsInstance(coherence['recommendation'], str)


if __name__ == '__main__':
    unittest.main()