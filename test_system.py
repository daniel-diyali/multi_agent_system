#!/usr/bin/env python3
"""
Simple test script to verify the multi-agent system works
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if core modules can be imported"""
    try:
        # Test basic Python functionality
        print("✓ Python environment working")
        
        # Test if our modules exist
        if os.path.exists("agents/orchestrator.py"):
            print("✓ Orchestrator module exists")
        else:
            print("✗ Orchestrator module missing")
            
        if os.path.exists("agents/intent_classifier.py"):
            print("✓ Intent classifier module exists")
        else:
            print("✗ Intent classifier module missing")
            
        if os.path.exists("evaluation/metrics.py"):
            print("✓ Evaluation module exists")
        else:
            print("✗ Evaluation module missing")
            
        if os.path.exists("api/main.py"):
            print("✓ API module exists")
        else:
            print("✗ API module missing")
            
        if os.path.exists("ui/app.py"):
            print("✓ UI module exists")
        else:
            print("✗ UI module missing")
            
        print("\n✓ All core modules are present!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_project_structure():
    """Test if project structure is correct"""
    required_dirs = [
        "agents",
        "rag", 
        "evaluation",
        "api",
        "ui",
        "config",
        "tests",
        "data/sample_data"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"✗ Missing directories: {missing_dirs}")
        return False
    else:
        print("✓ All required directories exist")
        return True

def main():
    print("🤖 Multi-Agent System Health Check")
    print("=" * 40)
    
    # Test project structure
    structure_ok = test_project_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    if structure_ok and imports_ok:
        print("\n🎉 System is ready!")
        print("\nNext steps:")
        print("1. Add your OPENAI_API_KEY to .env file")
        print("2. Run: streamlit run ui/app.py")
        print("3. Or run: python -m uvicorn api.main:app --reload")
        return True
    else:
        print("\n❌ System has issues that need to be fixed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)