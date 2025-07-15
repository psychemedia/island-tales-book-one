# island-tales-book-one
Island Tales, Book 1


BUILD:

https://github.com/tbroadley/spellchecker-cli\

spellchecker -l en-GB  --files  *.md --dictionaries _dictionary_godshill.txt  > spellingreport.txt

jb clean .

jb build --toc _toc_godshill.yml --config _config_godshill.yml --builder pdflatex .

jb build --toc _toc_puckaster.yml --config _config_puckaster.yml --builder pdflatex .
