#!/usr/bin/env python3
"""Test pickle support for HtmlString objects."""

import pickle
from rusty_tags import Div, HtmlString

def test_pickle_htmlstring():
    """Test that HtmlString objects can be pickled and unpickled."""
    
    # Create an HtmlString object
    html = Div("Hello, World!", cls="greeting")
    print(f"Original: {html}")
    print(f"Type: {type(html)}")
    
    # Test pickling
    try:
        pickled_data = pickle.dumps(html)
        print("✓ Pickling successful")
    except Exception as e:
        print(f"✗ Pickling failed: {e}")
        return False
    
    # Test unpickling
    try:
        unpickled_html = pickle.loads(pickled_data)
        print(f"Unpickled: {unpickled_html}")
        print(f"Type: {type(unpickled_html)}")
    except Exception as e:
        print(f"✗ Unpickling failed: {e}")
        return False
    
    # Verify content is the same
    if str(html) == str(unpickled_html):
        print("✓ Content matches after pickle/unpickle")
        return True
    else:
        print(f"✗ Content mismatch: '{html}' != '{unpickled_html}'")
        return False

def test_pickle_with_different_protocols():
    """Test pickling with different protocol versions."""
    html = Div("Test content", id="test")
    
    for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
        try:
            pickled = pickle.dumps(html, protocol=protocol)
            unpickled = pickle.loads(pickled)
            assert str(html) == str(unpickled)
            print(f"✓ Protocol {protocol} works")
        except Exception as e:
            print(f"✗ Protocol {protocol} failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing HtmlString pickle support...")
    print("=" * 50)
    
    success1 = test_pickle_htmlstring()
    print()
    success2 = test_pickle_with_different_protocols()
    
    if success1 and success2:
        print("\n✓ All pickle tests passed!")
    else:
        print("\n✗ Some pickle tests failed!")