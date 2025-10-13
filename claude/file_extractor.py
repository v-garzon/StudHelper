#!/usr/bin/env python3
"""
Enhanced File Extractor for StudHelper Backend Documentation
Extracts individual files from a consolidated documentation file.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Tuple
from enum import Enum

class FileAction(Enum):
    OVERWRITE = "overwrite"
    SKIP = "skip"
    RENAME = "rename"

class FileExtractor:
    def __init__(self, input_file: str, dest_folder: str = ".", 
                 interactive: bool = True, default_action: Optional[FileAction] = None):
        """
        Initialize the file extractor.
        
        Args:
            input_file: Path to the input documentation file
            dest_folder: Destination folder for extracted files
            interactive: Whether to prompt user for file conflicts
            default_action: Default action for file conflicts (for batch processing)
        """
        self.input_file = Path(input_file).resolve()
        self.dest_folder = Path(dest_folder).resolve()
        self.interactive = interactive
        self.default_action = default_action
        self.created_files = []
        self.skipped_files = []
        self.current_file = None
        self.content_started = False
        
        # File patterns
        self.file_patterns = [
            re.compile(r'^###\s+\d+\.\s+NEW\s+FILE:\s+(.+)$'),  # ### N. NEW FILE: [filepath / filename]
            re.compile(r'^###\s+\d+\.\s+MODIFIED\s+FILE:\s+(.+)$'),  # ### N. MODIFIED FILE: [filepath / filename]
            re.compile(r'^###\s+NEW\s+FILE:\s+(.+)$'),  # ### NEW FILE: [filepath / filename]
            re.compile(r'^###\s+MODIFIED\s+FILE:\s+(.+)$'),  # ### MODIFIED FILE: [filepath / filename]
        ]
        
        # Section headers to skip
        self.skip_patterns = [
            re.compile(r'^###\s+\d+\.\s+[A-Z][^:]*$'),  # Section headers without files
            re.compile(r'^###\s+[A-Z][^:]*$'),  # General section headers
        ]
    
    def validate_input(self) -> bool:
        """Validate input file exists."""
        if not self.input_file.exists():
            print(f"Error: File '{self.input_file}' not found")
            return False
        return True
    
    def setup_destination(self) -> None:
        """Create destination folder if it doesn't exist."""
        if not self.dest_folder.exists():
            self.dest_folder.mkdir(parents=True, exist_ok=True)
            print(f"Created destination folder: {self.dest_folder}")
    
    def get_file_action(self, file_path: Path) -> FileAction:
        """
        Determine what action to take for an existing file.
        
        Args:
            file_path: Path to the file that already exists
            
        Returns:
            FileAction to take
        """
        if not self.interactive and self.default_action:
            return self.default_action
        
        if not self.interactive:
            # Default behavior when not interactive
            return FileAction.SKIP
        
        print(f"\nFile already exists: {file_path}")
        print("What would you like to do?")
        print("1. Overwrite the existing file")
        print("2. Skip this file")
        print("3. Create with a new name (add suffix)")
        print("a. Apply to all remaining conflicts")
        
        while True:
            choice = input("Enter your choice (1/2/3/a): ").strip().lower()
            
            if choice == '1':
                return FileAction.OVERWRITE
            elif choice == '2':
                return FileAction.SKIP
            elif choice == '3':
                return FileAction.RENAME
            elif choice == 'a':
                print("\nChoose default action for all remaining conflicts:")
                print("1. Overwrite all")
                print("2. Skip all")
                print("3. Rename all")
                
                while True:
                    default_choice = input("Enter default choice (1/2/3): ").strip()
                    if default_choice == '1':
                        self.default_action = FileAction.OVERWRITE
                        self.interactive = False
                        return FileAction.OVERWRITE
                    elif default_choice == '2':
                        self.default_action = FileAction.SKIP
                        self.interactive = False
                        return FileAction.SKIP
                    elif default_choice == '3':
                        self.default_action = FileAction.RENAME
                        self.interactive = False
                        return FileAction.RENAME
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3.")
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 'a'.")
    
    def get_unique_filename(self, file_path: Path) -> Path:
        """
        Generate a unique filename by adding a suffix.
        
        Args:
            file_path: Original file path
            
        Returns:
            Unique file path
        """
        counter = 1
        stem = file_path.stem
        suffix = file_path.suffix
        
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = file_path.parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def extract_filename(self, line: str) -> Optional[str]:
        """
        Extract filename from a line using patterns.
        
        Args:
            line: Line to check
            
        Returns:
            Filename if found, None otherwise
        """
        for pattern in self.file_patterns:
            match = pattern.match(line.strip())
            if match:
                return match.group(1).strip()
        return None
    
    def should_skip_line(self, line: str) -> bool:
        """
        Check if line should be skipped (section headers).
        
        Args:
            line: Line to check
            
        Returns:
            True if line should be skipped
        """
        for pattern in self.skip_patterns:
            if pattern.match(line.strip()):
                return True
        return False
    
    def close_current_file(self) -> None:
        """Close current file and report creation."""
        if self.current_file:
            print(f"Created: {self.current_file.relative_to(self.dest_folder)}")
            self.created_files.append(self.current_file)
            self.current_file = None
            self.content_started = False
    
    def start_new_file(self, filename: str) -> bool:
        """
        Start writing to a new file.
        
        Args:
            filename: Name/path of the file to create
            
        Returns:
            True if file was created/opened, False if skipped
        """
        # Close previous file
        self.close_current_file()
        
        # Create file path
        file_path = self.dest_folder / filename
        
        # Create directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle existing files
        if file_path.exists():
            action = self.get_file_action(file_path)
            
            if action == FileAction.SKIP:
                print(f"Skipped: {file_path.relative_to(self.dest_folder)}")
                self.skipped_files.append(file_path)
                return False
            elif action == FileAction.RENAME:
                file_path = self.get_unique_filename(file_path)
                print(f"Creating with new name: {file_path.relative_to(self.dest_folder)}")
        
        # Set current file
        self.current_file = file_path
        self.content_started = False
        
        # Create/truncate the file
        with open(file_path, 'w', encoding='utf-8') as f:
            pass  # Just create empty file
        
        return True
            
    def write_to_current_file(self, line: str) -> None:
        """
        Write a line to the current file.
        
        Args:
            line: Line to write
        """
        if not self.current_file:
            return
        
        # Skip first empty line after file declaration
        if not self.content_started and not line.strip():
            self.content_started = True
            return
        
        self.content_started = True
        
        with open(self.current_file, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    
    def extract_files(self) -> None:
        """Main extraction logic."""
        print(f"Extracting files from {self.input_file.name} to {self.dest_folder}...")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n\r')
                
                # Check for new file declarations
                filename = self.extract_filename(line)
                if filename:
                    file_created = self.start_new_file(filename)
                    if not file_created:
                        # File was skipped, continue processing
                        continue
                    else:
                        # Regular file was created, continue processing
                        continue
                    
                elif self.should_skip_line(line):
                    # Skip section headers
                    continue
                
                # Write content to current file
                if self.current_file:
                    self.write_to_current_file(line)
        
        # Close final file
        self.close_current_file()
    
    def print_summary(self) -> None:
        """Print extraction summary."""
        print("\n" + "="*50)
        print("FILE EXTRACTION COMPLETE")
        print("="*50)
        
        print(f"\nFiles extracted to: {self.dest_folder}")
        
        if self.created_files:
            print(f"\nCreated files ({len(self.created_files)}):")
            for file_path in sorted(self.created_files):
                rel_path = file_path.relative_to(self.dest_folder)
                size = file_path.stat().st_size
                print(f"  ✓ {rel_path} ({size} bytes)")
        
        if self.skipped_files:
            print(f"\nSkipped files ({len(self.skipped_files)}):")
            for file_path in sorted(self.skipped_files):
                rel_path = file_path.relative_to(self.dest_folder)
                print(f"  ⏭ {rel_path}")
        
        # Show directory structure
        print(f"\nDirectory structure:")
        self._print_tree(self.dest_folder, max_depth=9)
        
        print("\nNext steps:")
        print("1. Review the created files")
        print("2. Set up Python virtual environment: python -m venv venv")
        print("3. Activate it: source venv/bin/activate (Unix) or venv\\Scripts\\activate (Windows)")
        print("4. Install dependencies: pip install -r requirements.txt")
        print("5. Configure environment: cp .env.example .env")
        print("6. Run the application")
    
    def _print_tree(self, directory: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> None:
        """Print directory tree structure."""
        if current_depth > max_depth:
            return
        
        def _exclude(p: Path) -> bool:
            if p.name == '__pycache__': return True
            if p.name == 'venv': return True
            if p.name == '.git': return True
            if p.name == '.idea': return True
            if p.name == '.vscode': return True
            if p.name == 'node_modules': return True
            if p.name == 'htmlcov': return True
            if p.name == 'uploads': return True
            return False
            
        items = sorted([p for p in directory.iterdir() if not _exclude(p)])
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth:
                next_prefix = prefix + ("    " if is_last else "│   ")
                self._print_tree(item, next_prefix, max_depth, current_depth + 1)

def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Extract files from StudHelper documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.py
  %(prog)s input.py --dest ./my_project
  %(prog)s input.py --dest /path/to/project --overwrite-all
  %(prog)s input.py --skip-all --quiet
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input documentation file to extract from'
    )
    
    parser.add_argument(
        '--dest', '-d',
        default='.',
        help='Destination folder for extracted files (default: current directory)'
    )
    
    parser.add_argument(
        '--overwrite-all',
        action='store_true',
        help='Overwrite all existing files without prompting'
    )
    
    parser.add_argument(
        '--skip-all',
        action='store_true',
        help='Skip all existing files without prompting'
    )
    
    parser.add_argument(
        '--rename-all',
        action='store_true',
        help='Rename all conflicting files without prompting'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress interactive prompts (use with --overwrite-all or --skip-all)'
    )
    
    args = parser.parse_args()
    
    # Determine default action and interactive mode
    interactive = not args.quiet
    default_action = None
    
    if args.overwrite_all:
        default_action = FileAction.OVERWRITE
        interactive = False
    elif args.skip_all:
        default_action = FileAction.SKIP
        interactive = False
    elif args.rename_all:
        default_action = FileAction.RENAME
        interactive = False
    
    # Create extractor
    extractor = FileExtractor(
        input_file=args.input_file,
        dest_folder=args.dest,
        interactive=interactive,
        default_action=default_action
    )
    
    # Validate and extract
    if not extractor.validate_input():
        sys.exit(1)
    
    try:
        extractor.setup_destination()
        extractor.extract_files()
        extractor.print_summary()
    except KeyboardInterrupt:
        print("\n\nExtraction cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during extraction: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()