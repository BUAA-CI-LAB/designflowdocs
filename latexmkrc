# latexmk main.tex: XeLaTeX -> PDF, all generated files go to build/.
$pdf_mode = 5;
$out_dir = 'build';
$xelatex = 'xelatex -no-shell-escape -synctex=1 -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$max_repeat = 5;
@default_files = ('main.tex');
