"""
Diagnostic script to test google-genai import and identify issues.
Run this to diagnose import problems.
"""

import sys

print("Python version:", sys.version)
print("Python path:", sys.executable)
print("\n" + "="*60)

# Check what's in the google namespace
print("\n1. Checking google namespace...")
try:
    import google
    print(f"   ✓ google module found at: {google.__file__ if hasattr(google, '__file__') else 'unknown'}")
    print(f"   ✓ google namespace contents: {[x for x in dir(google) if not x.startswith('_')]}")
except ImportError as e:
    print(f"   ✗ Cannot import google: {e}")
    sys.exit(1)

# Try to import genai
print("\n2. Attempting to import genai...")
try:
    from google import genai
    print(f"   ✓ Successfully imported genai!")
    print(f"   ✓ genai module location: {genai.__file__ if hasattr(genai, '__file__') else 'unknown'}")
    print(f"   ✓ genai.Client available: {hasattr(genai, 'Client')}")
    
    # Test creating a client (without API key)
    print("\n3. Testing Client creation...")
    try:
        # This will fail without API key, but we can check if the class exists
        client_class = genai.Client
        print(f"   ✓ genai.Client class found: {client_class}")
    except Exception as e:
        print(f"   ⚠ Client class check: {e}")
    
    print("\n" + "="*60)
    print("✓ All checks passed! The import is working correctly.")
    print("If agent_example_1.py still fails, the issue is elsewhere.")
    
except ImportError as e:
    print(f"   ✗ Failed to import genai: {e}")
    print("\n" + "="*60)
    print("DIAGNOSIS:")
    print("The google-genai package is not properly installed or there's a namespace conflict.")
    print("\nSOLUTION:")
    print("1. Activate your virtual environment")
    print("2. Run: pip uninstall google-generativeai")
    print("3. Run: pip uninstall google-genai")
    print("4. Run: pip install --upgrade google-genai")
    print("5. Run this script again to verify")
    sys.exit(1)

except Exception as e:
    print(f"   ✗ Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


