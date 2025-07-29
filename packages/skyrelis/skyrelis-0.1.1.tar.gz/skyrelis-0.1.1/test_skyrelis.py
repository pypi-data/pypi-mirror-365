#!/usr/bin/env python3
"""
Test script to validate Skyrelis package functionality before PyPI publication.
"""

import sys
import os

def test_basic_imports():
    """Test that all main components can be imported successfully."""
    print("🔍 Testing basic imports...")
    
    try:
        import skyrelis
        print(f"✅ Package imports: skyrelis v{skyrelis.__version__}")
        
        # Test main decorator import
        from skyrelis import observe
        print("✅ Main decorator available: observe")
        
        # Test all public API functions
        from skyrelis import (
            observe_langchain_agent,
            observe_agent, 
            quick_observe,
            quick_observe_class,
            send_trace,
            capture_agent_metadata
        )
        print("✅ All decorators available")
        
        # Test that observe is an alias for observe_langchain_agent
        assert observe == observe_langchain_agent
        print("✅ observe alias works correctly")
        
        print(f"📧 Contact: {skyrelis.__email__}")
        print(f"👥 Author: {skyrelis.__author__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_core_components():
    """Test that core internal components are available."""
    print("\n🔍 Testing core components...")
    
    try:
        # Test core imports (internal, but should work)
        from skyrelis.core.agent_observer import AgentObserver
        from skyrelis.core.monitored_agent import ObservabilityCallbackHandler
        from skyrelis.config.observer_config import ObserverConfig
        from skyrelis.utils.remote_observer_client import RemoteObserverClient
        
        print("✅ Core components available")
        
        # Test configuration creation
        config = ObserverConfig(
            remote_observer_url="https://test.example.com",
            agent_name="test_agent"
        )
        print("✅ Configuration creation works")
        
        return True
        
    except ImportError as e:
        print(f"❌ Core component import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Core component error: {e}")
        return False

def test_decorator_usage():
    """Test that decorators can be applied (without actual execution)."""
    print("\n🔍 Testing decorator usage...")
    
    try:
        from skyrelis import observe
        
        # Test class decoration (should not fail)
        @observe(monitor_url="https://test.example.com", agent_name="test_agent")
        class TestAgent:
            def __init__(self):
                pass
            
            def invoke(self, input_data):
                return "test response"
        
        print("✅ Class decorator applies successfully")
        
        # Test function decoration
        from skyrelis import observe_agent
        
        @observe_agent(monitor_url="https://test.example.com")
        def test_function(query):
            return f"Response to: {query}"
        
        print("✅ Function decorator applies successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Decorator usage error: {e}")
        return False

def test_package_structure():
    """Test that package structure is correct."""
    print("\n🔍 Testing package structure...")
    
    try:
        import skyrelis
        import skyrelis.core
        import skyrelis.utils
        import skyrelis.config
        
        print("✅ All modules available")
        
        # Check that __all__ is properly defined
        expected_public_api = [
            "observe",
            "observe_langchain_agent", 
            "observe_agent",
            "quick_observe",
            "quick_observe_class", 
            "send_trace",
            "capture_agent_metadata"
        ]
        
        for api_func in expected_public_api:
            assert hasattr(skyrelis, api_func), f"Missing public API: {api_func}"
        
        print("✅ Public API complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Package structure error: {e}")
        return False

def main():
    """Run all tests and report results."""
    print("🔒 Skyrelis AI Agent Security Library - Package Validation")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_core_components,
        test_decorator_usage,
        test_package_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("\n❌ Test failed - package may not be ready for publication")
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! Skyrelis package is ready for PyPI publication!")
        print("\nNext steps:")
        print("1. Build the package: python -m build")
        print("2. Upload to TestPyPI: python -m twine upload --repository testpypi dist/*")
        print("3. Test install: pip install --index-url https://test.pypi.org/simple/ skyrelis")
        print("4. Upload to PyPI: python -m twine upload dist/*")
        return 0
    else:
        print("\n❌ FAILED! Package needs fixes before publication")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 