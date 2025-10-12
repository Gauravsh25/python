#!/usr/bin/env python3
"""
Git pre-commit hook to detect and prevent committing sensitive credentials.
Place this file in .git/hooks/pre-commit and make it executable (chmod +x)
"""

import re
import sys
import subprocess

# Patterns to detect sensitive information
SENSITIVE_PATTERNS = {
    'AWS Access Key': r'AKIA[0-9A-Z]{16}',
    'AWS Secret Key': r'aws(.{0,20})?['\''"][0-9a-zA-Z\/+]{40}['\''"]',
    'Generic API Key': r'api[_-]?key['\''"\s:=]+[a-zA-Z0-9_\-]{20,}',
    'Generic Secret': r'secret['\''"\s:=]+[a-zA-Z0-9_\-]{20,}',
    'Password in Code': r'password['\''"\s:=]+[^\s]{8,}',
    'Private Key': r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
    'GitHub Token': r'gh[pousr]_[A-Za-z0-9_]{36,}',
    'Generic Token': r'token['\''"\s:=]+[a-zA-Z0-9_\-]{20,}',
    'Slack Token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}',
    'Google API Key': r'AIza[0-9A-Za-z_\-]{35}',
    'Bearer Token': r'Bearer\s+[a-zA-Z0-9_\-\.=]+',
    'Basic Auth': r'Basic\s+[A-Za-z0-9+/=]+',
    'Database URL': r'(mysql|postgresql|mongodb):\/\/[^\s:]+:[^\s@]+@',
    'Slack Webhook': r'https:\/\/hooks\.slack\.com\/services\/T[a-zA-Z0-9_]+\/B[a-zA-Z0-9_]+\/[a-zA-Z0-9_]+',
}

# Files to exclude from scanning
EXCLUDED_FILES = {
    '.gitignore',
    'package-lock.json',
    'yarn.lock',
    'poetry.lock',
}

# Extensions to exclude
EXCLUDED_EXTENSIONS = {
    '.min.js',
    '.min.css',
    '.map',
    '.lock',
}

def get_staged_files():
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        return [f for f in result.stdout.strip().split('\n') if f]
    except subprocess.CalledProcessError:
        return []

def should_scan_file(filename):
    """Check if file should be scanned."""
    if not filename:
        return False
    
    # Skip excluded files
    if any(excluded in filename for excluded in EXCLUDED_FILES):
        return False
    
    # Skip excluded extensions
    if any(filename.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
        return False
    
    return True

def get_file_content(filename):
    """Get content of staged file."""
    try:
        result = subprocess.run(
            ['git', 'show', f':{filename}'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except (subprocess.CalledProcessError, UnicodeDecodeError):
        # Skip binary files or files with encoding issues
        return None

def scan_content(filename, content):
    """Scan content for sensitive patterns."""
    findings = []
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern_name, pattern in SENSITIVE_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    'file': filename,
                    'line': line_num,
                    'pattern': pattern_name,
                    'content': line.strip()[:100]  # Show first 100 chars
                })
    
    return findings

def main():
    """Main function to run the pre-commit hook."""
    print("🔍 Scanning for sensitive credentials...")
    
    staged_files = get_staged_files()
    
    if not staged_files:
        print("✅ No files to scan.")
        return 0
    
    all_findings = []
    
    for filename in staged_files:
        if not should_scan_file(filename):
            continue
        
        content = get_file_content(filename)
        if content is None:
            continue
        
        findings = scan_content(filename, content)
        all_findings.extend(findings)
    
    if all_findings:
        print("\n❌ COMMIT REJECTED: Sensitive credentials detected!\n")
        print("=" * 70)
        
        for finding in all_findings:
            print(f"\n📁 File: {finding['file']}")
            print(f"📍 Line: {finding['line']}")
            print(f"🔑 Type: {finding['pattern']}")
            print(f"💡 Content: {finding['content']}")
        
        print("\n" + "=" * 70)
        print("\n⚠️  Please remove sensitive credentials before committing.")
        print("💡 Consider using environment variables or secret management tools.")
        print("💡 Add sensitive files to .gitignore if needed.\n")
        
        return 1
    
    print("✅ No sensitive credentials detected. Proceeding with commit.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
