#!/usr/bin/env python3
"""
Merge all generated markdown files into a single book with YAML cleaning
"""

import os
import re
import glob
from datetime import datetime

def clean_markdown_content(content):
    """
    Clean markdown content by removing or fixing problematic YAML metadata
    """
    lines = content.split('\n')
    cleaned_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 检测 YAML 元数据块 (以 --- 开头)
        if line.strip() == '---' and i == 0:
            # 跳过整个 YAML 块
            i += 1
            while i < len(lines) and lines[i].strip() != '---':
                i += 1
            if i < len(lines):  # 跳过结束的 ---
                i += 1
            continue
        
        # 移除其他可能的 YAML 片段
        if line.strip().startswith('---') and ':' in line:
            i += 1
            continue
            
        cleaned_lines.append(line)
        i += 1
    
    return '\n'.join(cleaned_lines)

def merge_markdown_files(input_dir="generated_book_chapters", output_file="complete_book.md"):
    """
    Merge all markdown files into a complete book
    """
    
    # Get all markdown files and sort them by chapter number
    md_files = glob.glob(os.path.join(input_dir, "Chapter*.md"))
    
    # Sort files by chapter number
    def extract_chapter_number(filename):
        match = re.search(r'Chapter(\d+)_(\d+)', filename)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return (0, 0)
    
    md_files.sort(key=extract_chapter_number)
    
    print(f"Found {len(md_files)} markdown files to merge")
    
    # Create book with proper YAML header for pandoc
    book_content = """---
title: "Statistical Physics Textbook: The Ising Model Approach"
author: "AI Generated"
date: "%s"
geometry: "margin=2.5cm"
toc: true
toc-depth: 2
numbersections: true
---

# Statistical Physics Textbook: The Ising Model Approach

*Generated on %s*  
*Total Chapters: %d*

## Table of Contents

""" % (datetime.now().strftime("%Y-%m-%d"), 
       datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
       len(md_files))
    
    # First pass: build table of contents
    toc_items = []
    for md_file in md_files:
        chapter_name = os.path.basename(md_file).replace('.md', '')
        match = re.search(r'Chapter(\d+)_(\d+)', chapter_name)
        if match:
            chapter_num = f"{match.group(1)}.{match.group(2)}"
            
            # Read file to get title (skip YAML metadata)
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                cleaned_content = clean_markdown_content(content)
                first_line = cleaned_content.split('\n')[0].strip() if cleaned_content else ""
                
                # Extract title from first header
                title = re.sub(r'^#+\s*', '', first_line)
                if not title or title == first_line:
                    title = f"Chapter {chapter_num}"
                
                toc_items.append((chapter_num, title))
    
    # Add TOC to book
    for chapter_num, title in toc_items:
        # Create anchor for TOC
        anchor = f"chapter-{chapter_num.replace('.', '-')}"
        book_content += f"- [{chapter_num} {title}](#{anchor})\n"
    
    book_content += "\n---\n\n"
    
    # Second pass: merge all cleaned content
    for i, md_file in enumerate(md_files, 1):
        print(f"Merging: {os.path.basename(md_file)}")
        
        chapter_name = os.path.basename(md_file).replace('.md', '')
        match = re.search(r'Chapter(\d+)_(\d+)', chapter_name)
        if match:
            chapter_num = f"{match.group(1)}.{match.group(2)}"
            
        # Add chapter separator with anchor
        book_content += f'\n<div id="chapter-{chapter_num.replace(".", "-")}"></div>\n\n'
        book_content += f"# Chapter {chapter_num}\n\n"
        
        # Read, clean and add file content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            cleaned_content = clean_markdown_content(content)
            
            # Remove the original title if it exists
            lines = cleaned_content.split('\n')
            if lines and re.match(r'^#+\s', lines[0]):
                lines = lines[1:]  # 移除原标题
            
            # Ensure proper heading levels (convert to level 2 and below)
            processed_content = []
            for line in lines:
                if line.startswith('# '):
                    processed_content.append('## ' + line[2:])
                elif line.startswith('## '):
                    processed_content.append('### ' + line[3:])
                elif line.startswith('### '):
                    processed_content.append('#### ' + line[4:])
                else:
                    processed_content.append(line)
            
            book_content += '\n'.join(processed_content) + "\n\n"
    
    # Save merged book
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(book_content)
    
    print(f"Book successfully merged into: {output_file}")
    print(f"Total files merged: {len(md_files)}")
    print(f"Book size: {len(book_content)} characters")
    
    return output_file

def create_ebook_formats(book_file="complete_book.md"):
    """
    Create additional ebook formats using pandoc with error handling
    """
    try:
        import subprocess
        
        # 首先验证 pandoc 是否可用
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Pandoc is not properly installed or not in PATH")
            return
        
        print("Pandoc found, starting conversion...")
        
        # Convert to PDF with robust error handling
        print("Converting to PDF...")
        pdf_result = subprocess.run([
            'pandoc', book_file, 
            '-o', 'complete_book.pdf',
            '--pdf-engine=xelatex',
            '-V', 'mainfont=Times New Roman',
            '--toc', '--toc-depth=2',
            '--fail-if-warnings'  # 严格模式，遇到警告会失败
        ], capture_output=True, text=True)
        
        if pdf_result.returncode == 0:
            print("PDF created successfully: complete_book.pdf")
        else:
            print("PDF creation failed")
            print("Error:", pdf_result.stderr)
            # 尝试更简单的PDF生成
            print("Trying simpler PDF generation...")
            subprocess.run([
                'pandoc', book_file,
                '-o', 'complete_book_simple.pdf',
                '--toc'
            ])
            print("Simple PDF created: complete_book_simple.pdf")
        
        # Convert to EPUB
        print("Converting to EPUB...")
        epub_result = subprocess.run([
            'pandoc', book_file,
            '-o', 'complete_book.epub',
            '--toc', '--toc-depth=2'
        ], capture_output=True, text=True)
        
        if epub_result.returncode == 0:
            print("EPUB created successfully: complete_book.epub")
        else:
            print("EPUB creation failed")
            print("Error:", epub_result.stderr)
        
        # Convert to DOCX (作为备用)
        print("Converting to DOCX...")
        subprocess.run([
            'pandoc', book_file,
            '-o', 'complete_book.docx'
        ])
        print("DOCX created: complete_book.docx")
        
    except Exception as e:
        print(f"Error in ebook conversion: {e}")
        print("Please ensure pandoc is properly installed:")
        print("Windows: Download from https://pandoc.org/installing.html")
        print("Linux: sudo apt-get install pandoc")
        print("macOS: brew install pandoc")

def check_pandoc_installation():
    """检查pandoc是否正确安装"""
    try:
        import subprocess
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(" Pandoc is properly installed")
            print(f"Pandoc version: {result.stdout.split()[1]}")
            return True
        else:
            print("Pandoc is not working properly")
            return False
    except FileNotFoundError:
        print("Pandoc is not installed or not in PATH")
        print("Please install pandoc from: https://pandoc.org/installing.html")
        return False

if __name__ == "__main__":
    input_dir = input("Enter input directory (default: generated_book_chapters): ").strip() or "generated_book_chapters"
    output_file = input("Enter output filename (default: complete_book.md): ").strip() or "complete_book.md"
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        exit(1)
    
    # 合并文件
    merged_file = merge_markdown_files(input_dir, output_file)
    
    # 检查pandoc安装
    if check_pandoc_installation():
        # 询问是否创建电子书格式
        create_ebook = input("Create PDF/EPUB formats? (y/n): ").strip().lower()
        if create_ebook in ['y', 'yes']:
            create_ebook_formats(merged_file)
    else:
        print("Skipping ebook format creation due to pandoc issues")