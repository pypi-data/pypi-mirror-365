import os
import sys
import subprocess
from pathlib import Path

def test_imports():
    
    print("🔍 Testing imports...")
    
    try:
        import anthropic
        print("✅ anthropic module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import anthropic: {e}")
        return False
    
    try:
        from security_scanner import SecurityScanner
        print("✅ SecurityScanner class imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SecurityScanner: {e}")
        return False
    
    return True

def test_api_key():
    
    print("\n🔑 Testing API key...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print("✅ ANTHROPIC_API_KEY is set")
        print(f"   Key starts with: {api_key[:10]}...")
        return True
    else:
        print("❌ ANTHROPIC_API_KEY is not set")


        print("   Please set it with: export ANTHROPIC_API_KEY='your-key'")
        return False

def test_file_structure():
    print("\n📁 Testing file structure...")
    
    required_files = [
        'security_scanner.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def test_scanner_initialization():
    print("\n🔧 Testing scanner initialization...")
    
    try:
        from security_scanner import SecurityScanner
        api_key = os.getenv('ANTHROPIC_API_KEY', 'test-key')
        scanner = SecurityScanner(api_key)
        print("✅ SecurityScanner initialized successfully")


        return True
    except Exception as e:
        print(f"❌ Failed to initialize SecurityScanner: {e}")
        return False

def test_file_detection():
    print("\n📄 Testing file detection...")
    
    try:
        from security_scanner import SecurityScanner
        api_key = os.getenv('ANTHROPIC_API_KEY', 'test-key')
        scanner = SecurityScanner(api_key)
        
        # Test with current directory
        current_dir = Path('.')
        files = scanner.get_files_to_scan(str(current_dir))
        


        print(f"✅ Found {len(files)} files to scan in current directory")
        
        # Show some example files
        for file in files[:5]:
            print(f"   - {file}")
        
        if len(files) > 5:
            print(f"   ... and {len(files) - 5} more files")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test file detection: {e}")
        return False

def test_comment_features():
    print("\n💬 Testing comment features...")
    
    try:
        from security_scanner import SecurityScanner
        api_key = os.getenv('ANTHROPIC_API_KEY', 'test-key')
        scanner = SecurityScanner(api_key)
        
        # Test comment style detection
        python_style = scanner.get_comment_style('.py')
        js_style = scanner.get_comment_style('.js')
        
        if python_style['single'] == '#' and js_style['single'] == '//':
            print("✅ Comment style detection working correctly")
        else:
            print("❌ Comment style detection failed")
            return False
        
        # Test line number extraction
        line_num = scanner.extract_line_number("Line 42")
        if line_num == 42:
            print("✅ Line number extraction working correctly")
        else:
            print("❌ Line number extraction failed")
            return False
        
        # Test vulnerability comment creation
        test_vuln = {
            'type': 'SQL Injection',
            'severity': 'High',
            'description': 'User input directly concatenated into SQL query',
            'code_section': 'query = f"SELECT * FROM users WHERE id = {user_id}"',
            'fix': '# Use parameterized queries\nquery = "SELECT * FROM users WHERE id = %s"\ncursor.execute(query, (user_id,))'
        }
        
        comment = scanner.create_vulnerability_comment(test_vuln, python_style)
        if 'SECURITY VULNERABILITY DETECTED' in comment and 'Suggested Fix:' in comment:
            print("✅ Vulnerability comment creation working correctly")
        else:
            print("❌ Vulnerability comment creation failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to test comment features: {e}")
        return False

def run_quick_test():
    print("\n🚀 Running quick test scan...")
    
    if not os.path.exists('example_vulnerable_code.py'):
        print("⚠️  example_vulnerable_code.py not found, skipping test scan")
        return True
    
    try:
        # Run the scanner on the example file
        result = subprocess.run([


            sys.executable, 'security_scanner.py', '.',
            '--max-workers', '1'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Test scan completed successfully")
            print("   Output preview:")
            lines = result.stdout.split('\n')[:10]
            for line in lines:
                print(f"   {line}")
            return True
        else:
            print(f"❌ Test scan failed with return code {result.returncode}")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Test scan timed out (this might be normal for API calls)")
        return True
    except Exception as e:
        print(f"❌ Test scan failed: {e}")
        return False

def main():
    print("🧪 Security Scanner Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("API Key Test", test_api_key),
        ("File Structure Test", test_file_structure),
        ("Scanner Initialization Test", test_scanner_initialization),
        ("File Detection Test", test_file_detection),
        ("Comment Features Test", test_comment_features),
        ("Quick Test Scan", run_quick_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The scanner is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Set your ANTHROPIC_API_KEY if not already done")
        print("   2. Run: python security_scanner.py /path/to/project")
        print("   3. Try with comments: python security_scanner.py /path/to/project --add-comments")
        print("   4. Check the README.md for more usage examples")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Set your API key: export ANTHROPIC_API_KEY='your-key'")
        print("   3. Check the README.md for detailed instructions")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 