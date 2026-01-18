#!/usr/bin/env python3
"""
Skill Validator

Validates Agent Skills (SKILL.md files) against the Agent Skills standard.
Checks for required frontmatter, proper formatting, and common issues.

Usage:
    python validate-skill.py <path-to-skill-directory>
    python validate-skill.py .github/skills/my-skill/
"""

import sys
import os
import re
from pathlib import Path

class SkillValidator:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.skill_md_path = self.skill_path / "SKILL.md"
        
    def validate(self):
        """Run all validation checks"""
        print(f"Validating skill at: {self.skill_path}")
        print("-" * 60)
        
        self.check_skill_md_exists()
        if not self.skill_md_path.exists():
            self.print_results()
            return False
            
        content = self.skill_md_path.read_text(encoding='utf-8')
        
        self.check_frontmatter(content)
        self.check_content_structure(content)
        self.check_directory_name()
        self.check_supporting_files()
        
        self.print_results()
        return len(self.errors) == 0
        
    def check_skill_md_exists(self):
        """Check if SKILL.md file exists with exact casing"""
        if not self.skill_md_path.exists():
            self.errors.append("SKILL.md file not found (must be exactly 'SKILL.md', not 'skill.md' or 'Skill.md')")
            return False
        return True
        
    def check_frontmatter(self, content):
        """Validate YAML frontmatter"""
        # Check for frontmatter delimiters
        if not content.startswith('---'):
            self.errors.append("Missing YAML frontmatter (must start with '---')")
            return
            
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.errors.append("Incomplete YAML frontmatter (must have closing '---')")
            return
            
        frontmatter = parts[1].strip()
        
        # Check for required 'name' field
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if not name_match:
            self.errors.append("Missing required 'name' field in frontmatter")
        else:
            name = name_match.group(1).strip()
            # Validate name format (lowercase, hyphens)
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                self.errors.append(f"Invalid name format '{name}' (must be lowercase with hyphens, e.g., 'my-skill-name')")
                
        # Check for required 'description' field
        description_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
        if not description_match:
            self.errors.append("Missing required 'description' field in frontmatter")
        else:
            description = description_match.group(1).strip()
            if len(description) < 20:
                self.warnings.append(f"Description is very short ({len(description)} chars). Consider adding more detail about when to use this skill.")
                
        # Check for optional 'license' field
        license_match = re.search(r'^license:\s*(.+)$', frontmatter, re.MULTILINE)
        if not license_match:
            self.warnings.append("No 'license' field specified (optional but recommended)")
            
    def check_content_structure(self, content):
        """Check for recommended content sections"""
        # Extract body (after frontmatter)
        parts = content.split('---', 2)
        if len(parts) < 3:
            return
        body = parts[2]
        
        # Check for heading
        if not re.search(r'^#\s+.+', body, re.MULTILINE):
            self.warnings.append("No main heading found (recommended: # Skill Title)")
            
        # Check for code examples
        if '```' not in body:
            self.warnings.append("No code blocks found. Consider adding examples for clarity.")
            
        # Check for numbered steps
        if not re.search(r'^\d+\.', body, re.MULTILINE):
            self.warnings.append("No numbered steps found. Consider using numbered lists for procedures.")
            
        # Check for "when to use" section
        if not re.search(r'when\s+to\s+use', body, re.IGNORECASE):
            self.warnings.append("No 'When to Use' section found. This helps agents know when to apply this skill.")
            
        # Check for examples section
        if not re.search(r'##\s+examples?', body, re.IGNORECASE):
            self.warnings.append("No 'Examples' section found. Examples greatly improve skill effectiveness.")
            
    def check_directory_name(self):
        """Check if directory name follows conventions"""
        dir_name = self.skill_path.name
        
        # Check lowercase with hyphens
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', dir_name):
            self.errors.append(f"Directory name '{dir_name}' should be lowercase with hyphens (e.g., 'my-skill-name')")
            
        # Check if directory name matches skill name in frontmatter
        if self.skill_md_path.exists():
            content = self.skill_md_path.read_text(encoding='utf-8')
            name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
            if name_match:
                skill_name = name_match.group(1).strip()
                if dir_name != skill_name:
                    self.warnings.append(f"Directory name '{dir_name}' doesn't match skill name '{skill_name}' in frontmatter")
                    
    def check_supporting_files(self):
        """Check for supporting files and provide guidance"""
        files = list(self.skill_path.iterdir())
        
        if len(files) == 1:  # Only SKILL.md
            self.warnings.append("No supporting files found. Consider adding examples, scripts, or templates if applicable.")
        else:
            # Check if supporting files are referenced in SKILL.md
            content = self.skill_md_path.read_text(encoding='utf-8')
            for file in files:
                if file.name != "SKILL.md" and file.is_file():
                    if file.name not in content:
                        self.warnings.append(f"Supporting file '{file.name}' is not referenced in SKILL.md")
                        
    def print_results(self):
        """Print validation results"""
        print()
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"   • {error}")
            print()
            
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
            
        if not self.errors and not self.warnings:
            print("✅ Skill validation passed! No issues found.")
            print()
        elif not self.errors:
            print("✅ No errors found. Warnings are recommendations only.")
            print()
        else:
            print(f"❌ Validation failed with {len(self.errors)} error(s).")
            print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate-skill.py <path-to-skill-directory>")
        print("Example: python validate-skill.py .github/skills/my-skill/")
        sys.exit(1)
        
    skill_path = sys.argv[1]
    
    if not os.path.isdir(skill_path):
        print(f"Error: '{skill_path}' is not a directory")
        sys.exit(1)
        
    validator = SkillValidator(skill_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
