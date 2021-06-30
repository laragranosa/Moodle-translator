#!/bin/bash

#tekst unutar ovih tagova se ne prevodi
blacklist_tags=('question type')

#tekst unutar ovih tagova obavezno se prevode
whitelist_tags=('text' 'questiontext' 'answertext' 'correctfeedback' 'partiallycorrectfeedback' 'incorrectfeedback')

source_file='./ulaz2.xml'
target_file='./ulaz2(en).xml'
languages_file='./jezici.txt'
target_language="en"

python3 translator.py $source_file $target_file $languages_file $target_language
