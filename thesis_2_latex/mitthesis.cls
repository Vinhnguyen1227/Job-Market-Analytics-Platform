\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{mitthesis}[1999/10/20]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions\relax
\LoadClass{report}

% Basic definitions to make the main file compile
\def\department#1{\gdef\@department{#1}}
\def\degree#1{\gdef\@degree{#1}}
\def\degreemonth#1{\gdef\@degreemonth{#1}}
\def\degreeyear#1{\gdef\@degreeyear{#1}}
\def\thesisdate#1{\gdef\@thesisdate{#1}}

\renewcommand{\cleardoublepage}{\clearpage\if@twoside \ifodd\c@page\else
    \hbox{}\newpage\if@twocolumn\hbox{}\newpage\fi\fi\fi}

\newenvironment{abstractpage}{\cleardoublepage\thispagestyle{empty}}{\cleardoublepage}

% To avoid errors from main.tex
\newcommand{\mainmatter}{}
