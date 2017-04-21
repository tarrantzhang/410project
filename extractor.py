import textract
import sys
import metapy

def whatisthis(s):
    if isinstance(s, str):
        print "ordinary string"
    elif isinstance(s, unicode):
        print "unicode string"
    else:
        print "not a string"

def extract_keywords(keyword_list, resource):
    word_list = get_word_list(resource,1) + get_word_list(resource,2) + get_word_list(resource,3)
    keywords = []
    for keyword in keyword_list:
        if keyword in word_list:
            keywords.append(keyword)
    return keywords

def get_word_list(text, ngram):
    doc = metapy.index.Document()
    doc.content(text)
    tok = metapy.analyzers.ICUTokenizer(True)
    tok = metapy.analyzers.LowercaseFilter(tok)
    tok.set_content(doc.content())
    ana = metapy.analyzers.NGramWordAnalyzer(ngram, tok)
    result = ana.analyze(doc)
    l = []
    for s in result:
        if isinstance(s,tuple):
            w = ' '.join(s);
            l.append(w.encode('utf-8'))
            ## add possible mutant word to list if s contants punctuation, rectify ICUTokenizer
            punc_list = ['+','#','/','\\','!','@','?','$','%','^','&']
            for punc in punc_list:
                if punc in w:
                    w = rectify_punctuation(w,punc)
            l.append(w.encode('utf-8'))
        else:
            l.append(s.encode('utf-8'))
    return l

def rectify_punctuation(word, punc):
    word = word.replace(" "+punc+" ", punc)
    word = word.replace(" "+punc, punc)
    word = word.replace(punc+" ", punc)
    return word

def process_keyword_list(keyword_path):
    l = []
    with open(keyword_path) as terms_file:
        for term in terms_file:
            l.append(term.strip().lower())
    return l

if len(sys.argv) < 2:
    print 'usage: python extractor.py resume.pdf keywords.txt'
text = textract.process(sys.argv[1])
text = unicode(text,'utf-8')
keyword_list = process_keyword_list(sys.argv[2])
print extract_keywords(keyword_list,text)
