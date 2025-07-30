#!/usr/bin/env python3
"""
Security Code Scanner using Claude API
Scans a project directory for security vulnerabilities and provides fixes.
"""

import os
import sys
import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class SecurityScanner:
    def __init__(self, api_key: str, max_workers: int = 4):
        """Initialize the security scanner with Claude API key."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.max_workers = max_workers
        
        # File extensions to scan
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cxx', 
            '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
            '.scala', '.clj', '.hs', '.ml', '.fs', '.sql', '.sh', '.bash',
            '.ps1', '.vbs', '.pl', '.r', '.m', '.scm', '.lisp', '.el'
        }
        
        # Directories to skip
        self.skip_dirs = {
            '.git', '.svn', '.hg', '__pycache__', 'node_modules', '.venv',
            'venv', 'env', '.env', 'build', 'dist', 'target', 'bin', 'obj',
            '.idea', '.vscode', '.vs', 'coverage', '.pytest_cache'
        }
        
        # File patterns to skip
        self.skip_files = {
            'package-lock.json', 'yarn.lock', 'poetry.lock', 'requirements.txt',
            '.gitignore', '.env.example', 'README.md', 'LICENSE'
        }

    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if a file should be scanned based on extension and path."""
        # Skip hidden files
        if file_path.name.startswith('.'):
            return False
            
        # Skip files in skip list
        if file_path.name in self.skip_files:
            return False
            
        # Skip files in skip directories
        for part in file_path.parts:
            if part in self.skip_dirs:
                return False
                
        # Only scan files with code extensions
        return file_path.suffix.lower() in self.code_extensions

    def get_files_to_scan(self, project_path: str) -> List[Path]:
        """Get all files that should be scanned in the project directory."""
        project_dir = Path(project_path)
        if not project_dir.exists():
            raise FileNotFoundError(f"Project directory not found: {project_path}")
            
        files_to_scan = []
        for file_path in project_dir.rglob('*'):
            if file_path.is_file() and self.should_scan_file(file_path):
                files_to_scan.append(file_path)
                
        return files_to_scan

    def read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {e}"

    def analyze_file_security(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for security vulnerabilities using Claude API."""
        try:
            content = self.read_file_content(file_path)
            if not content or content.startswith("Error reading file:"):
                return {
                    'file_path': str(file_path),
                    'error': content if content.startswith("Error reading file:") else "Empty file",
                    'vulnerabilities': [],
                    'suggestions': []
                }

            # Prepare the prompt for Claude
            prompt = f"""You are a security expert analyzing code for vulnerabilities. Analyze the following {file_path.suffix} file for security issues.

File: {file_path.name}
Path: {file_path}

Code:
```{file_path.suffix}
{content}
```

Please identify:
1. Security vulnerabilities (SQL injection, XSS, CSRF, path traversal, etc.)
2. Unsafe practices (hardcoded secrets, weak crypto, etc.)
3. Potential security issues

For each finding, provide:
- Vulnerability type and severity (High/Medium/Low)
- Line number or code section
- Description of the issue
- The vulnerable code section
- Suggested fix with commented code that can be added as comments

Format your response as JSON:
{{
    "vulnerabilities": [
        {{
            "type": "vulnerability_type",
            "severity": "High/Medium/Low",
            "line": "line_number_or_section",
            "description": "description",
            "code_section": "vulnerable_code",
            "fix": "commented_fix_code_with_proper_comment_syntax"
        }}
    ],
    "summary": "brief_summary"
}}

Important for fix suggestions:
- Provide the fix code with proper comment syntax for the file type
- Make the fix code ready to be added as comments in the source file
- Include explanatory comments within the fix code
- Show both the vulnerable pattern and the secure alternative

Focus on real security issues, not style or performance concerns."""

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the response
            try:
                # Extract JSON from response
                content = response.content[0].text
                
                # Try multiple approaches to extract JSON
                result = None
                
                # Method 1: Try to find JSON with regex
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
                
                # Method 2: If regex failed, try to find JSON boundaries more precisely
                if not result:
                    # Look for the start and end of JSON
                    start_idx = content.find('{')
                    if start_idx != -1:
                        # Find matching closing brace
                        brace_count = 0
                        end_idx = start_idx
                        for i, char in enumerate(content[start_idx:], start_idx):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = i
                                    break
                        
                        if end_idx > start_idx:
                            try:
                                json_str = content[start_idx:end_idx + 1]
                                result = json.loads(json_str)
                            except json.JSONDecodeError:
                                pass
                
                # Method 3: Try to fix common JSON issues and parse
                if not result:
                    try:
                        # Replace problematic triple quotes with escaped quotes
                        fixed_content = content.replace('"""', '\\"\\"\\"')
                        result = json.loads(fixed_content.strip())
                    except json.JSONDecodeError:
                        pass
                
                # Method 4: If still no result, try to parse the entire content as JSON
                if not result:
                    try:
                        result = json.loads(content.strip())
                    except json.JSONDecodeError:
                        pass
                
                # Method 5: Manual parsing as last resort
                if not result:
                    try:
                        # Try to manually extract vulnerabilities from the response
                        vulnerabilities = []
                        
                        # Look for vulnerability patterns in the response
                        vuln_patterns = [
                            r'"type":\s*"([^"]+)"',
                            r'"severity":\s*"([^"]+)"',
                            r'"line":\s*"([^"]+)"',
                            r'"description":\s*"([^"]+)"'
                        ]
                        
                        # Extract basic vulnerability info
                        types = re.findall(r'"type":\s*"([^"]+)"', content)
                        severities = re.findall(r'"severity":\s*"([^"]+)"', content)
                        lines = re.findall(r'"line":\s*"([^"]+)"', content)
                        descriptions = re.findall(r'"description":\s*"([^"]+)"', content)
                        
                        # Create vulnerabilities from extracted data
                        for i in range(min(len(types), len(severities), len(lines), len(descriptions))):
                            vulnerabilities.append({
                                "type": types[i],
                                "severity": severities[i],
                                "line": lines[i],
                                "description": descriptions[i],
                                "code_section": "",
                                "fix": ""
                            })
                        
                        if vulnerabilities:
                            result = {
                                "vulnerabilities": vulnerabilities,
                                "summary": "Manually extracted from response"
                            }
                    except Exception:
                        pass
                
                # If all methods failed, create a fallback result
                if not result:
                    result = {
                        "vulnerabilities": [],
                        "summary": "Could not parse response",
                        "raw_response": content
                    }
                    
            except json.JSONDecodeError as e:
                result = {
                    "vulnerabilities": [],
                    "summary": f"Invalid JSON response: {str(e)}",
                    "raw_response": content
                }

            return {
                'file_path': str(file_path),
                'vulnerabilities': result.get('vulnerabilities', []),
                'summary': result.get('summary', ''),
                'raw_response': result.get('raw_response', '')
            }

        except Exception as e:
            return {
                'file_path': str(file_path),
                'error': str(e),
                'vulnerabilities': [],
                'suggestions': []
            }

    def scan_project(self, project_path: str) -> Dict[str, Any]:
        """Scan the entire project for security vulnerabilities."""
        print(f"🔍 Scanning project: {project_path}")
        
        # Get files to scan
        files_to_scan = self.get_files_to_scan(project_path)
        print(f"📁 Found {len(files_to_scan)} files to scan")
        
        if not files_to_scan:
            print("⚠️  No files found to scan")
            return {'files_analyzed': 0, 'results': []}
        
        results = []
        files_with_vulnerabilities = 0
        
        # Scan files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze_file_security, file_path): file_path 
                for file_path in files_to_scan
            }
            
            for i, future in enumerate(as_completed(future_to_file), 1):
                file_path = future_to_file[future]
                print(f"📄 Analyzing ({i}/{len(files_to_scan)}): {file_path.name}")
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.get('vulnerabilities'):
                        files_with_vulnerabilities += 1
                        
                except Exception as e:
                    print(f"❌ Error analyzing {file_path}: {e}")
                    results.append({
                        'file_path': str(file_path),
                        'error': str(e),
                        'vulnerabilities': []
                    })
        
        return {
            'files_analyzed': len(files_to_scan),
            'files_with_vulnerabilities': files_with_vulnerabilities,
            'results': results
        }

    def print_results(self, scan_results: Dict[str, Any]):
        """Print the scan results in a formatted way."""
        print("\n" + "="*80)
        print("🔒 SECURITY SCAN RESULTS")
        print("="*80)
        
        files_analyzed = scan_results['files_analyzed']
        files_with_vulns = scan_results['files_with_vulnerabilities']
        
        print(f"\n📊 Summary:")
        print(f"   Files analyzed: {files_analyzed}")
        print(f"   Files with vulnerabilities: {files_with_vulns}")
        print(f"   Vulnerability rate: {(files_with_vulns/files_analyzed*100):.1f}%" if files_analyzed > 0 else "   Vulnerability rate: N/A")
        
        total_vulns = 0
        high_vulns = 0
        medium_vulns = 0
        low_vulns = 0
        
        # Process results
        for result in scan_results['results']:
            if result.get('error'):
                print(f"\n❌ Error in {result['file_path']}: {result['error']}")
                continue
                
            vulnerabilities = result.get('vulnerabilities', [])
            if not vulnerabilities:
                continue
                
            print(f"\n🔍 {result['file_path']}")
            print("-" * 60)
            
            for vuln in vulnerabilities:
                total_vulns += 1
                severity = vuln.get('severity', 'Unknown').upper()
                
                if severity == 'HIGH':
                    high_vulns += 1
                    severity_icon = "🔴"
                elif severity == 'MEDIUM':
                    medium_vulns += 1
                    severity_icon = "🟡"
                else:
                    low_vulns += 1
                    severity_icon = "🟢"
                
                print(f"\n{severity_icon} {severity} - {vuln.get('type', 'Unknown vulnerability')}")
                print(f"   Line/Section: {vuln.get('line', 'N/A')}")
                print(f"   Description: {vuln.get('description', 'No description')}")
                
                if vuln.get('code_section'):
                    print(f"   Vulnerable Code:")
                    print(f"   {vuln['code_section']}")
                
                if vuln.get('fix'):
                    print(f"   Suggested Fix:")
                    print(f"   {vuln['fix']}")
        
        # Print summary
        print(f"\n" + "="*80)
        print("📈 VULNERABILITY SUMMARY")
        print("="*80)
        print(f"   Total vulnerabilities found: {total_vulns}")
        print(f"   High severity: {high_vulns}")
        print(f"   Medium severity: {medium_vulns}")
        print(f"   Low severity: {low_vulns}")
        
        if total_vulns == 0:
            print("\n✅ No security vulnerabilities found!")
        else:
            print(f"\n⚠️  {total_vulns} security issues found. Please review and fix them.")

def main():
    """Main function to run the security scanner."""
    parser = argparse.ArgumentParser(
        description="Security Code Scanner using Claude API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python security_scanner.py /path/to/project
  python security_scanner.py . --max-workers 8
  python security_scanner.py /path/to/project --output results.json
        """
    )
    
    parser.add_argument(
        'project_path',
        help='Path to the project directory to scan'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of parallel workers (default: 4)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file to save results as JSON'
    )
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key:")
        print("export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    try:
        # Initialize scanner
        scanner = SecurityScanner(api_key, args.max_workers)
        
        # Scan project
        start_time = time.time()
        scan_results = scanner.scan_project(args.project_path)
        end_time = time.time()
        
        # Print results
        scanner.print_results(scan_results)
        
        # Save results if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(scan_results, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")
        
        print(f"\n⏱️  Scan completed in {end_time - start_time:.2f} seconds")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 

