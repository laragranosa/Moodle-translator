import re
from textblob import TextBlob
import sys

""" UPUTA """
""" na Smartcatu prilikom učitavanja višejezične datoteke koja se želi prevesti, potrebno je odabrati opciju
    split into segments 'tags- and attributes-based' s uključenim 'protect HTML tags in CDATA section'
    a) Prilikom spajanja dviju JEDNOjezičnih datoteka, poziv programa iz naredbenog retka treba biti u obliku
    'python3 Samrtcat_merge.py source_file1 source_file2 target_file "" ' -> 4. argument ostaviti prazno, inače se u njega upisuje odredišni jezik.
    b) Prilikom spajanja dviju VIŠEjezičnih datoteka, poziv programa iz naredbenog retka treba biti u obliku
    ' python3 Samrtcat_merge.py source_file1 source_file2 target_file "target_lang" ' -> kao 4. argument OBAVEZNO upisati kraticu odredišnog jezika(npr. "de") 
"""

def main():
    ulaz1=[]
    ulaz2=[]
    relevant_tags = ['text', 'questiontext', 'answertext', 'correctfeedback', 'partiallycorrectfeedback', 'incorrectfeedback']
    to_remove = ['<p>', '</p>', ']]>', '<![CDATA[', '&lt', 'p&gt', ';', ';br', '/p&gt', '&gt', '/ p&gt']
    to_replace = ['="multilang" ','=" multilang "','=" multilang"','="multilang "','= "multilang"', '="multilang"']
    target_lang = sys.argv[4]
    fp = open(sys.argv[3], "w", encoding="utf-8")
    with open(sys.argv[1], "r", encoding="utf-8") as a_file:
        pom_str=''

        # u sljedećoj for petlji retci iz neprevedene ulazne datoteke se redom obrađuju i spremaju u listu
        # na način da se tekst prelomljen na više redaka sprema kao jedan izraz(jedan element liste) ili
        # ako se u retku ulazne datoteke nalaze isključivo 2 html stringa(bez teksta), razdvajaju se da je svaki zaseban element liste
        for line in a_file:
            p = re.compile('|'.join(map(re.escape, to_remove)))
            l1 = p.sub('', line.strip())
            line = line.lstrip()
            if (re.match(r'<(.*)></(.*)>', l1.strip()) != None and l1.count('lang=')<2):
                ulaz1.append(str(l1.strip().split('><')[0]) + '>')
                ulaz1.append('<' + str(l1.strip().split('><')[1]))
            elif (re.match(r'<(.*)>(.+)\n', line) != None):
                ulaz1.append(l1)
                indeks = ulaz1.index(l1)
            elif (re.match(r'(.+)<(.*)>', line) != None):
                pom_str += ' '.join(ulaz1[-(len(ulaz1) - indeks):])
                pom_str += line
                ulaz1[indeks] = pom_str
                ulaz1 = ulaz1[:(indeks + 1)]
            else:
                if l1 != '':
                    ulaz1.append(l1)
    with open(sys.argv[2], "r", encoding="utf-8") as b_file:

        # u sljedećoj for petlji retci iz prevedene ulazne datoteke se redom obrađuju i spremaju u listu
        for line in b_file:
            p = re.compile('|'.join(map(re.escape, to_remove)))
            l2 = p.sub('', line.strip())
            l2=l2.replace('lang =','lang=')
            l2 = l2.replace('lang= ', 'lang=')
            if l2.count('lang=')>=2:
                p = re.compile('|'.join(map(re.escape, to_replace)))
                l2 = p.sub('="multilang" ', l2.strip())
                l2=l2.replace('" >', '">')
                l2=l2.replace('< / span>','</span>')
                l2=l2.replace('< span', '</span')
                l2=l2.replace('</span class', '<span class')
                l2=l2.replace('/span> <span', '/span><span')
                l2=l2.replace('"  lang', '" lang')
                match = re.match(r'.*<(.*)><span class="multilang" lang="hr">(.*?)</span>(.*)', l2)
                if (match != None):
                    tag= match.group(1)
                    textphrase2 = match.group(2)
                    ulaz2.append('<' + tag + '>' + str(textphrase2) + '<' + tag + '/>')
            elif (re.match(r'<(.*)></(.*)>', l2.strip()) != None):
                ulaz2.append(str(l2.strip().split('><')[0]) + '>')
                ulaz2.append('<' + str(l2.strip().split('><')[1]))
            else:
                if l2!= '':
                    ulaz2.append(l2)
    if (len(ulaz1) != len(ulaz2)):
        print('Neispravne ulazne datoteke!')
        exit(1)

    #spajanje izraza iz ulazne neprevedene datoteke s pripadajućim prevedenim izrazom iz ulazne prevedene datoteke
    for i in range(len(ulaz1)):
        tag=''
        p = re.compile('|'.join(map(re.escape, to_remove)))
        l1 = p.sub('', ulaz1[i].strip())
        l2 = p.sub('', ulaz2[i].strip())
        if ' + ' in l2:
            l2=l2.replace(' + ','+')
        if ' + ' in l1:
            l1=l1.replace(' + ','+')
        else:
            if l1==l2:
                fp.write(l1 + '\n')
            else:
                if (re.search('<(.+?)>(.*)', l1) != None):
                    tag = re.search('<(.+?)>', l1).group(1)

                if l1.count('lang=') >= 2: #spajanje izraza i formatiranje zapisa za izlaznu datoteku, ako se radi o višejezičnom izrazu iz ulazne datoteke
                    if (re.search('<(.+?)>(.*)', l2) != None):
                        tag2 = re.search('<(.+?)>', l2).group(1)
                    l2=l2.replace('<' + tag2 + '/>', '</' + tag2 + '>')
                    textphrase2 = l2.replace('<' + tag + '>', '').replace('</' + tag + '>', '').strip()
                    target_lang=TextBlob(textphrase2).detect_language()
                    new_line=l1[:-(len(tag)+3)] + '<span class="multilang" lang="' + target_lang + '">' + textphrase2 + '</span></text>'
                else: #spajanje izraza i formatiranje zapisa za izlaznu datoteku, ako se radi o jednojezičnom izrazu iz ulazne datoteke
                    textphrase1 = l1.replace('<' + tag + '>', '').replace('</' + tag + '>', '').strip()
                    textphrase2 = l2.replace('<' + tag + '>', '').replace('</' + tag + '>', '').strip()
                    target_lang = TextBlob(textphrase2).detect_language()
                    new_line = '<' + tag + '><![CDATA[<span class="multilang" lang="hr">'+textphrase1+'</span><span class="multilang" lang="' + target_lang + '">'+ textphrase2 +'</span>]]></' + tag + '>'
                fp.write(new_line + '\n')

main()