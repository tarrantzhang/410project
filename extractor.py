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
    word_list_1 = get_word_list(resource,1)
    word_list_2 = get_word_list(resource,2)
    word_list_3 = get_word_list(resource,3)
    keywords = []
    for keyword in keyword_list:
        if len(keyword.split(' ')) == 1:
            if keyword in word_list_1:
                keywords.append(keyword)
        elif len(keyword.split(' ')) == 2:
            if keyword in word_list_2:
                keywords.append(keyword)
        elif len(keyword.split(' ')) == 3:
            if keyword in word_list_3:
                keywords.append(keyword)
    return keywords

def get_word_list(text, ngram):
    doc = metapy.index.Document()
    doc.content(text)
    tok = metapy.analyzers.ICUTokenizer()
    tok = metapy.analyzers.LowercaseFilter(tok)
    tok.set_content(doc.content())
    ana = metapy.analyzers.NGramWordAnalyzer(ngram, tok)
    result = ana.analyze(doc)
    l = []
    for s in result:
        if isinstance(s,tuple):
            l.append(' '.join(s).encode('utf-8'))
        else:
            l.append(s.encode('utf-8'))
    return l

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
