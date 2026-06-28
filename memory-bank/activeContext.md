# Active Context

## Active Goal
* Manually refine and compile `thesis_1.tex` to match final layout requirements.

## Current State
* Restructured Chapters 1 and 2 in `thesis_1.tex` and corresponding Markdown files (`thesis_1_introduction.md`, `thesis_1_objectives.md`) to move the Literature Review to Chapter 2 ("Objective and Literature Review") and keep Chapter 1 focused on Introduction and Contributions.
* Added a new `1.4 Scientific and Technical Contributions` section to Chapter 1 of Thesis 1.
* Toned down overclaimed Problem Statements and Research Questions in Chapter 1, and synced these changes with Chapters 4 and 5 in `thesis_1.tex` and markdown files (`thesis_1_results_discussion.md`, `thesis_1_conclusion.md`).
* Rebuilt the Word document (`thesis_1.docx` and `thesis_1.doc`) successfully using `build_thesis_1_doc.py`.
* Compiled updated `thesis_1.tex` successfully using local Tectonic compiler (`.\thesis_2_latex\tectonic.exe`) to generate the final `thesis_1.pdf`.
* Checked all table values manually against `thesis_1_content.docx`. Verified all data is correct and matches.
* Corrected author name to `Nguyễn Phú Vinh` on cover page and certificate.
* Updated supervisor names on the cover page: External Supervisor: MS Nguyễn Xuân Thịnh, Internal Supervisor: Dr. Giang Anh Tuấn.
* Unbolded all `\textbf{}` text inside paragraphs while preserving bolding in headings, captions, signature blocks, tables, and the title page.
* Replaced all em-dashes (`—`) with standard hyphens (`-`) across the entire document.
* Copied the actual university logo file `usth logo.png` from My Drive into the project root as `logoUSTH.png`, so it renders correctly on the cover page.
* Removed redundant `Table X:` prefixes from tables 1-5 captions to fix duplicate label rendering in PDF output.
* Removed unsupported checkmark emoji characters from tables to prevent font compilation warnings.
* Deleted the Python LaTeX generation scripts (`build_thesis_1_latex.py` and `convert_thesis.py`).
* Fixed layout overflows: wrapped Table 6 in a resizebox, split Section 3.5.1 pipeline flow equation across lines, and added line breaks in Section 1.2.3 heading to respect page margins.
* Replaced the text-based appendices (ASCII folder tree, env vars, GitHub actions workflow) with actual screenshots of the Homepage, AI Assistant, My Profile, and Market Insights pages (correctly ordered).
* Copied 16 new diagrams drawn by the user from `G:\My Drive\thesis_images\phan da sua thesis 1` to `d:\Job-Market-Analytics-Platform\thesis_1_images` to replace old version diagrams in the PDF.
* Applied mismatches and style fixes from `thesis_mismatches_fix_guide.md` to `thesis_1.tex`, including Times New Roman font setup, global italics disabling, heading parentheses removal, table text enlargement and cell wrapping, and factual updates (Qdrant vectors, Electra NER, Elasticsearch search fields, geographical cities mapping).
* Resolved table styling issues: set table text sizes to 12pt (normalsize), left-aligned cell formatting using a new `L` column type, resolved Table 3, 4, 6, 7 page margin overflows, and unified typewriter font settings to match Times New Roman.
* Converted all 11 tables in `thesis_1.tex` to `tabularx` layout, making them stretch exactly to the page layout width (`\textwidth`) with proportional left-aligned `Z` columns.

## Next Steps
* Final review of the PDF print layout quality and structure.

## Recent Updates
* Restructured Section 3.5.1 data flow from arrow equation style to detailed text description in both [chapter_8_thesis_1.md](file:///d:/Job-Market-Analytics-Platform/chapter_8_thesis_1.md) and [thesis_1.tex](file:///d:/Job-Market-Analytics-Platform/thesis_1.tex).
* Verified that all figure captions in [thesis_1.tex](file:///d:/Job-Market-Analytics-Platform/thesis_1.tex) and [thesis_1_front_matter.md](file:///d:/Job-Market-Analytics-Platform/thesis_1_front_matter.md) contain no section numbers (e.g., "Figure 13: Multi-adapter orchestrator architecture").
* Moved ACKNOWLEDGEMENTS and LIST OF ABBREVIATIONS before Table of Contents in [thesis_1.tex](file:///d:/Job-Market-Analytics-Platform/thesis_1.tex) to conform to USTH layout standard.
* Cleaned up figure captions in [thesis_1.tex](file:///d:/Job-Market-Analytics-Platform/thesis_1.tex) to remove redundant title descriptions under the `\textmd` tag and formatted them cleanly with colons.
* Changed hyperlink fonts in LaTeX references to Times New Roman by setting \urlstyle{same} in the preamble of [thesis_1.tex](file:///d:/Job-Market-Analytics-Platform/thesis_1.tex).
* Removed unused abbreviations (CI/CD, GHA, USTH) from both [thesis_1_front_matter.md](file:///d:/Job-Market-Analytics-Platform/thesis_1_front_matter.md) and [thesis_1.tex](file:///d:/Job-Market-Analytics-Platform/thesis_1.tex) to clean up the List of Abbreviations.
* Successfully rebuilt the Word document ([thesis_1.docx](file:///d:/Job-Market-Analytics-Platform/thesis_1.docx) and [thesis_1.doc](file:///d:/Job-Market-Analytics-Platform/thesis_1.doc)) and compiled the PDF ([thesis_1.pdf](file:///d:/Job-Market-Analytics-Platform/thesis_1.pdf)) with no compilation errors.
