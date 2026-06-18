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
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # Non-greedy match for code blocks
    text = re.sub(r'```(\w+)?\n(.*?)\n```', code_repl, md_text, flags=re.DOTALL)
    
    # Inline code
    inline_codes = []
    def inline_repl(match):
        inline_codes.append(match.group(1))
        return f"__INLINE_CODE_{len(inline_codes)-1}__"
    text = re.sub(r'`([^`]+)`', inline_repl, text)

    # Chapters
    text = re.sub(r'^#\s*(?:Chapter\s*\d+:\s*)?(.*)$', r'\\chapter{\1}', text, flags=re.MULTILINE)
    
    # Sections
    text = re.sub(r'^##\s*(?:\d+\.\d+\s*)?(.*)$', r'\\section{\1}', text, flags=re.MULTILINE)
    
    # Subsections
    text = re.sub(r'^###\s*(?:\d+\.\d+\.\d+\s*)?(.*)$', r'\\subsection{\1}', text, flags=re.MULTILINE)
    
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    
    # Italic
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    text = re.sub(r'_(.*?)_', r'\\textit{\1}', text)
    
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\\href{\2}{\1}', text)
    
    # Lists (simple approach)
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
        text = text.replace(f"__INLINE_CODE_{i}__", f"\\texttt{{{code}}}")
        
    # Restore code blocks
    for i, (lang, code) in enumerate(code_blocks):
        block = f"\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}"
        text = text.replace(f"__CODE_BLOCK_{i}__", block)
        
    # Replace special latex characters outside of code blocks? Too complex, let's keep it simple.
    # At least replace '&' with '\&' if not in math, but let's just do a basic one.
    # Actually, we can just leave it to the user or do basic escaping later.
    
    return text

def main():
    output_dir = "thesis_2_latex"
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all chapter files for thesis 2
    chapter_files = glob.glob("chapter_*_thesis_2.md")
    chapter_files.sort()
    
    chapters = []
    
    for file in chapter_files:
        with open(file, 'r', encoding='utf-8') as f:
            md_text = f.read()
            
        latex_text = md_to_latex(md_text)
        
        # Determine output filename
        base_name = os.path.basename(file).replace('.md', '.tex')
        chapters.append(base_name)
        
        with open(os.path.join(output_dir, base_name), 'w', encoding='utf-8') as f:
            f.write(latex_text)
            
        print(f"Converted {file} -> {base_name}")
        
    # Generate main.tex
    main_tex = """\\documentclass[12pt,vi,twoside]{mitthesis}
\\usepackage{lmodern}
\\usepackage[T1]{fontenc}
\\usepackage{graphicx}
\\usepackage{hyperref}
\\usepackage{float}

\\title{Job Market Analytics Platform \\\\ Technical Implementation and Architecture}
\\author{Author}
\\department{Department of Computer Science}
\\degree{Bachelor of Science}
\\degreemonth{June}
\\degreeyear{2026}
\\thesisdate{June 18, 2026}

\\begin{document}
\\maketitle
\\cleardoublepage

\\tableofcontents
\\cleardoublepage

\\mainmatter
"""
    for ch in chapters:
        main_tex += f"\\include{{{ch.replace('.tex', '')}}}\n"
        
    main_tex += "\\end{document}\n"
    
    with open(os.path.join(output_dir, 'main.tex'), 'w', encoding='utf-8') as f:
        f.write(main_tex)
        
    print("Generated main.tex")

if __name__ == "__main__":
    main()
