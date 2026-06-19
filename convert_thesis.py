import re
import os
import glob

def md_to_latex(md_text):
    # Process code blocks first so we don't mess up their contents
    code_blocks = []
    def code_repl(match):
        lang = match.group(1) or ""
        code = match.group(2)
        code_blocks.append((lang, code))
        return f"CODEBLOCKPLACEHOLDER{len(code_blocks)-1}Q"
    
    text = re.sub(r'```(\w+)?\n(.*?)\n```', code_repl, md_text, flags=re.DOTALL)
    
    # Inline code
    inline_codes = []
    def inline_repl(match):
        inline_codes.append(match.group(1))
        return f"INLINECODEPLACEHOLDER{len(inline_codes)-1}Q"
    text = re.sub(r'`([^`]+)`', inline_repl, text)

    # Subsections
    text = re.sub(r'^###\s*(?:\d+\.\d+\.\d+\s*)?(.*)$', r'\\subsection{\1}', text, flags=re.MULTILINE)
    
    # Sections
    text = re.sub(r'^##\s*(?:\d+\.\d+\s*)?(.*)$', r'\\section{\1}', text, flags=re.MULTILINE)

    # Chapters
    text = re.sub(r'^#\s+(?:Chapter\s*\d+:\s*)?(.*)$', r'\\chapter{\1}', text, flags=re.MULTILINE)
    
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    
    # Italic
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    text = re.sub(r'_(.*?)_', r'\\textit{\1}', text)
    
    # Escape special chars
    text = text.replace('&', '\\&')
    text = text.replace('%', '\\%')
    text = text.replace('_', '\\_')
    text = text.replace('$', '\\$')
    
    # Lists
    lines = text.split('\n')
    in_itemize = False
    in_enumerate = False
    out_lines = []
    for line in lines:
        if line.startswith('- ') or line.startswith('* '):
            if not in_itemize:
                out_lines.append(r'\begin{itemize}')
                in_itemize = True
            item_text = line[2:]
            out_lines.append(f'\\item {item_text}')
        elif re.match(r'^\d+\.\s', line):
            if not in_enumerate:
                out_lines.append(r'\begin{enumerate}')
                in_enumerate = True
            item_text = re.sub(r'^\d+\.\s', '', line)
            out_lines.append(f'\\item {item_text}')
        else:
            if in_itemize:
                out_lines.append(r'\end{itemize}')
                in_itemize = False
            if in_enumerate:
                out_lines.append(r'\end{enumerate}')
                in_enumerate = False
            out_lines.append(line)
            
    if in_itemize:
        out_lines.append(r'\end{itemize}')
    if in_enumerate:
        out_lines.append(r'\end{enumerate}')
        
    text = '\n'.join(out_lines)
    
    # Restore inline code
    for i, code in enumerate(inline_codes):
        code_esc = code.replace('&', '\\&').replace('%', '\\%').replace('_', '\\_').replace('$', '\\$')
        text = text.replace(f"INLINECODEPLACEHOLDER{i}Q", f"\\texttt{{{code_esc}}}")
        
    # Restore code blocks
    for i, (lang, code) in enumerate(code_blocks):
        block = f"\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}"
        text = text.replace(f"CODEBLOCKPLACEHOLDER{i}Q", block)
        
    return text

def main():
    output_dir = "thesis_2_latex"
    os.makedirs(output_dir, exist_ok=True)
    
    chapter_files = glob.glob("chapter_*_thesis_2.md")
    chapter_files.sort()
    
    chapters = []
    
    for file in chapter_files:
        with open(file, 'r', encoding='utf-8') as f:
            md_text = f.read()
            
        latex_text = md_to_latex(md_text)
        base_name = os.path.basename(file).replace('.md', '.tex')
        chapters.append(base_name)
        
        with open(os.path.join(output_dir, base_name), 'w', encoding='utf-8') as f:
            f.write(latex_text)
            
        print(f"Converted {file} -> {base_name}")

if __name__ == "__main__":
    main()
