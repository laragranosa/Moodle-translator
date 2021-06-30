from __future__ import with_statement
import re
from textblob import TextBlob
import time
import sys
from urllib.error import HTTPError



""" UPUTA """
""" Prilikom pokretanja programa iz naredbenog retka, kao prvi argument navodi se putanja datoteke koju se želi prevesti,
    kao drugi argument navodi se datoteka u koju želimo pohraniti prevedeni sadržaj, a 
    kao treći argument potrebno je navesti odredišni jezik na koji se datoteka želi prevesti.
    primjer: python3 translator.py source_file target_file "target_language"
"""

def multilanguage_string (textphrase, tag, target_lang):
    global warning
    global warning_word
    warning=0
    if flag==1: #ako je izraz višejezičan
        if '="multilang"' in stripped_line:
            mymatch = re.match('.*<' + tag + '><span class="multilang" lang="hr">(.*)</span>(.*)', stripped_line)  # izdvajanje dijela teksta koji je potrebno prevesti
        elif 'xml:lang' in stripped_line:
            mymatch = re.match(r'.*<' + tag + '><span (.*) lang="hr">(.*?)</span>(.*)', stripped_line) #izdvajanje dijela teksta koji je potrebno prevesti
        textphrase2 = textphrase
        textphrase = mymatch.group(1)
        if '="multilang"' in textphrase or 'xml:lang' in textphrase:
            textphrase = textphrase[:textphrase.index('</span>')]
    for i in textphrase[:-1].split():
        if len(i)>=3:
            if TextBlob(i).detect_language() == 'en':
                warning=1
                warning_word = i
    neprevedeno = TextBlob(textphrase)
    if (len(textphrase.strip()) <= 0) :
        full_translation = '<' + tag + '></' + tag + '>'
    elif (textphrase.isupper()) or (len(textphrase.strip()) <= 2) or (neprevedeno.detect_language() == target_lang):
        full_translation = '<' + tag + '><![CDATA[<span class="multilang" lang="hr">'+textphrase+'</span><span class="multilang" lang="' + target_lang + '">'+textphrase+'</span>]]></' + tag + '>'
    else:
        time.sleep(1)
        if flag==1: #prevođenje teksta iz višejezičnog izraza i formatiranje prevedenog za zapis u izlaznu datoteku
            translation = neprevedeno.translate(from_lang='hr', to=target_lang)
            full_translation = textphrase2[:-(len(tag)+3)] + '<span class="multilang" lang="' + target_lang + '">' + str(translation) + '</span></text>'
        else: #prevođenje teksta iz jednojezičnog izraza i formatiranje prevedenog za zapis u izlaznu datoteku
            translation = neprevedeno.translate(from_lang='hr', to=target_lang)
            if 'ahref' in translation:
                translation = translation.replace('ahref', 'a href')
            full_translation = '<' + tag + '><![CDATA[<span class="multilang" lang="hr">'+textphrase+'</span><span class="multilang" lang="' + target_lang + '">'+str(translation)+'</span>]]></' + tag + '>'
    global br
    print("Trenutno obrađeno: {0:2.2f}% ulazne datoteke".format(100.00 * br / len(ulaz1)))
    if warning==1:
        print('Upozorenje u retku ' + str(br) +',redak sadrži riječ koja nije na izvornom jeziku: ' + warning_word + '!')
    return full_translation


try:
    with open(sys.argv[3], "r", encoding="utf-8") as jezici:
        ispravni_jezici = jezici.read().split('\n')
except EnvironmentError:
    print('Neispravna ulazna datoteka jezici!')
    exit(1)

target_lang = sys.argv[4].lower()
if target_lang not in ispravni_jezici:
    print('Neispravno zadan jezik!')
    exit(1)
else:
    print('Ulazna datoteka se prevodi...')
fp = open(sys.argv[2], "w+", encoding="utf-8")
try:
    with open(sys.argv[1], "r", encoding="utf-8") as a_file:
        pom_str=''
        ulaz1=[]
        to_remove = ['<p>', '</p>', ']]>', '<![CDATA[', '&lt', 'p&gt', ';br', ';' , '/p&gt', '&gt', '<b>', '</b>', '<span xml:lang="hr" lang="hr">', '<br>']
        blacklist_tags=['question type']
        whitelist_tags=['text', 'questiontext', 'answertext', 'correctfeedback', 'partiallycorrectfeedback', 'incorrectfeedback'] #tekst unutar ovih tagova je obavezno prevesti
        pom_str = ''

        for line in a_file:
            p = re.compile('|'.join(map(re.escape, to_remove))) #uklanjanje suvišnih ili pogrešno umetnutih tagova
            l1 = p.sub('', line.strip())
            line = line.lstrip()

            if (re.match(r'(.*)</span>(.*)</span>', line) != None):
                l1 = l1.replace('</span>', '')

            # ispitivanje cjelovitosti izraza (nije dio prelomljenog teksta ili se radi o html tagu bez teksta koji je potrebno prevesti)
            if (re.match(r'<(.*)></(.*)>', l1.strip()) != None and l1.count('lang=') < 2):
                ulaz1.append(str(l1.strip().split('><')[0]) + '>')
                ulaz1.append('<' + str(l1.strip().split('><')[1]))
            # ispitivanje odgovara li izraz tekstu prelomljenom na vise redaka
            elif (re.match(r'<(.*)>(.+)\n', line) != None):
                ulaz1.append(l1)
                indeks = ulaz1.index(l1)
            # ispitivanje je li izraz posljednji dio prelomljenog teksta
            elif (re.match(r'(.+)<(.*)>', line) != None):
                pom_str += ' '.join(ulaz1[-(len(ulaz1) - indeks):])
                pom_str +=' '
                pom_str += l1
                ulaz1[indeks] = pom_str
                ulaz1 = ulaz1[:(indeks + 1)]
            else: #izraz je cisti html tag, ne sadrzi tekst koji je potrebno prevesti
                if l1 != '':
                    ulaz1.append(l1)

        global br
        global warning
        global warning_word
        br=0
        print("Trenutno obrađeno: {0:2.2f}% ulazne datoteke".format(100.00 * br / len(ulaz1)))
        #u listi ulaz1 nalaze se svi retci ulazne datoteke, sređeni za prevođenje
        for stripped_line in ulaz1:
            br+=1
            tag=''
            flag=0
            black_flag=0

            if (re.search('<(.*) (.*)>(.*)', stripped_line) != None):
                a = re.search('<(.*) (.*)>', stripped_line).group(0)
                for i in blacklist_tags:
                    if i in a:
                        fp.write(stripped_line + '\n')
                        black_flag=1

            if (re.search('<(.+?)>(.*)', stripped_line) != None and re.search('<(.+?)>(.*)', stripped_line).group(1) in whitelist_tags):
                tag = re.search('<(.+?)>', stripped_line).group(1)

            #provjera je li izraz višejezičan kako bi se izdvojio i preveo samo dio teksta koji odgovara izvornom jeziku
            if stripped_line.count('lang=')>=2:
                flag=1
                new_line = multilanguage_string(stripped_line, tag, target_lang) #prevođenje
                new_line = '<' + tag + '><![CDATA[' + new_line[(len(tag)+3):-(len(tag)+3)] + ']]></' + tag + '>' #formatiranje ispisa
                if warning == 1:
                    new_line =new_line + '  WARNING!-' + warning_word
                fp.write(new_line + '\n')
            else: #dio koda za jednojezične izraze
                mymatch = re.match(r'.*<' + tag + '>(.*)</'+tag+'>', stripped_line) #ispitivanje sadrži li izraz tekst koji je potrebno prevesti
                if (mymatch): #ako sadrži, tekst se prevodi
                    new_line = multilanguage_string ( mymatch.group(1), tag, target_lang)
                    if warning == 1:
                        new_line = new_line + '  WARNING!-' + warning_word
                    fp.write(new_line + '\n')
                else: #ako ne sadrži, izravan zapis u datoteku bez prevođenja
                    if black_flag == 0:
                        fp.write(stripped_line + '\n')

    fp.close()
    print('Datoteka je prevedena!')

except HTTPError:
    print('Dosegnut dnevni limit TextBlob biblioteke!')
    exit(1)
except EnvironmentError:
    print('Neispravna ulazna datoteka!')
    exit(1)
