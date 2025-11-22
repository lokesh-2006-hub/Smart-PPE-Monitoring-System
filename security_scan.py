#!/usr/bin/env python3
"""
Security Scanner - Finds potential secrets in your code
Run before pushing to GitHub!
"""

import os
import re

# Patterns to search for
PATTERNS = {
    'passwords': [
        r'password\s*=\s*["\']([^"\']+)["\']',
        r'PASSWORD\s*=\s*["\']([^"\']+)["\']',
        r'pwd\s*=\s*["\']([^"\']+)["\']',
    ],
    'emails': [
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    ],
    'api_keys': [
        r'api[_-]?key\s*=\s*["\']([^"\']+)["\']',
        r'secret[_-]?key\s*=\s*["\']([^"\']+)["\']',
    ],
    'database_urls': [
        r'mysql://[^"\'\s]+',
        r'postgresql://[^"\'\s]+',
    ]
}

# Directories to skip
SKIP_DIRS = {'venv', 'node_modules', '__pycache__', '.git', 'dist', 'build'}

# Files to skip
SKIP_FILES = {'.env.example', 'security_scan.py', 'SECURITY.md'}

def scan_file(filepath):
    """Scan a single file for secrets"""
    findings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            for category, patterns in PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        findings.append({
                            'file': filepath,
                            'line': line_num,
                            'category': category,
                            'match': match.group(0)[:50]  # Truncate long matches
                        })
    except Exception as e:
        pass  # Skip files that can't be read
    
    return findings

def scan_directory(root_dir):
    """Recursively scan directory for secrets"""
    all_findings = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        
        for filename in filenames:
            # Skip binary files and excluded files
            if filename in SKIP_FILES or not filename.endswith(('.py', '.js', '.jsx', '.env', '.json', '.yaml', '.yml', '.txt')):
                continue
            
            filepath = os.path.join(dirpath, filename)
            findings = scan_file(filepath)
            all_findings.extend(findings)
    
    return all_findings

if __name__ == '__main__':
    print("🔍 Scanning for potential secrets...\n")
    
    # Scan current directory
    findings = scan_directory('.')
    
    if not findings:
        print("✅ No obvious secrets found!")
        print("\nNote: This is a basic scan. Always review your code manually.")
    else:
        print(f"⚠️  Found {len(findings)} potential secrets:\n")
        
        for finding in findings:
            print(f"  📁 {finding['file']}:{finding['line']}")
            print(f"     Category: {finding['category']}")
            print(f"     Match: {finding['match']}")
            print()
        
        print("\n⚠️  Review these findings before pushing to GitHub!")
        print("💡 Use environment variables for sensitive data")
    
    # Check if .env is in .gitignore
    try:
        with open('.gitignore', 'r') as f:
            if '.env' in f.read():
                print("\n✅ .env is in .gitignore")
            else:
                print("\n❌ WARNING: .env is NOT in .gitignore!")
    except:
        print("\n❌ WARNING: .gitignore file not found!")
