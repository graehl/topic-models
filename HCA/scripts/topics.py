#!/usr/bin/env python

###

usage = """
Given input documents (plain text with space separated tokens), output one per line a list of topics characterized by words characteristic of the topic.
"""

def options():
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument(option_strings=[], dest='docs', nargs='*', metavar='FILE')
    parser.add_argument('-s', '--stopwords', type=str, dest='stopwords', metavar='FILE')
    parser.add_argument('-0', '--allow-nonalpha', type=boolarg, dest='allow_nonalpha')
    parser.add_argument('-t', '--tokenize', type=boolarg, dest='tokenize', help='add spaces between alphabetic word parts')
    parser.add_argument('-c', '--sentences', type=boolarg, dest='sentences', help='input within doc is assumed to be sentences one per line - see --downcase')
    parser.add_argument('-d', '--downcase', type=boolarg, dest='downcase', help='lowercase the input (if --sentences, lowercase only the first word)')
    parser.add_argument('-S', '--cased-stopwords', type=boolarg, dest='cased_stopwords', help='stopwords are case-sensitive')
    parser.add_argument('-m', '--min-chars', type=int, dest='min_chars')
    parser.add_argument('-M', '--max-chars', type=int, dest='max_chars')
    parser.add_argument('-v', '--verbose', type=int, dest='verbose')
    parser.add_argument('-o', '--stem', type=str, dest='stem')
    parser.add_argument('-l', '--topic-length', type=int, dest='topic_length')
    parser.add_argument('-k', '--classes', type=int, metavar='NUM', dest='classes')
    parser.add_argument('-q', '--quality', type=float, metavar='0-10', dest='quality')
    parser.add_argument('-B', '--hca-burst', type=float, metavar='0-inf', dest='hca_burst', help='strength of topic burtiness model e.g. 0.01. 0 = disable burstiness.')
    parser.add_argument('-b', '--hca-bin', type=str, metavar='EXEFILE', dest='hca_bin')
    parser.add_argument('-r', '--hca-rank', type=str, metavar='idf|rat', dest='hca_rank', help='for naming topics, use IDF or likelihood ratio (rat) to select words especially typical of a topic')
    parser.add_argument('-N', '--name-length', type=int, metavar='NUM', dest='name_length', help='for naming topics, maximum length in words')
    parser.set_defaults(hca_bin=hcabin, verbose=0, hca_rank='idf', name_length=10, hca_burst=0, quality=3, classes=5, length=10, cased_stopwords=False, downcase=False, sentences=True, tokenize=True, allow_nonalpha=False, min_chars=3, max_chars=18, stopwords='SCRIPTDIR/rouge_155.txt', stem='docs', eod=EOD_line)
    return parser


###

import argparse
def boolarg(v):
  return v.lower() in ("yes", "true", "t", "1")

import sys, os, re

import six
# Conversion between Unicode and UTF-8, if required (on Python2)
_native_to_unicode = (lambda s: s.decode("utf-8")) if six.PY2 else (lambda s: s)
# Conversion between Unicode and UTF-8, if required (on Python2)
_unicode_to_native = (lambda s: s.encode("utf-8")) if six.PY2 else (lambda s: s)

def to_unicode(s):
    if six.PY2 and isinstance(s, str):
        return s.decode("utf-8")
    return s

def ustrlen(s):
    return len(to_unicode(s))

import gzip

def opengz(filename, mode='r'):
    return (gzip.open if filename.endswith('.gz') else open)(filename, mode)

spacere=re.compile(r'\s+')
def singlespace(s):
    s = spacere.sub(' ', s)
    if s.endswith(' '):
        s = s[:-1]
    return s[1:] if s.startswith(' ') else s

def chomp(s):
    return s.rstrip('\r\n')

global_logging = os.environ.get('DEBUG', '')
global_logging = int(global_logging) if len(global_logging) else 0
global_logging_once = False

def log(s, v=1, out=sys.stderr, logging=global_logging):
    global global_logging_once
    if not global_logging_once:
        if global_logging > 0:
            out.write("### DEBUG=%s\n" % global_logging)
        global_logging_once = True
    if logging >= v:
        out.write("### "+s+"\n")

basename = os.path.basename

import errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def mkdir_parent(filename):
    mkdir_p(os.path.dirname(filename))

def chomped_file(filename):
    for line in opengz(filename):
        yield chomp(line)


scriptdir = os.path.realpath(os.path.dirname(sys.argv[0]))

import tokenizer

def fileSCRIPTDIR(f):
    sd = 'SCRIPTDIR'
    if f.startswith(sd):
        return scriptdir + '/' + f[len(sd):]
    return f

hcadir = scriptdir + "/../hca"
hcabin = hcadir + "/hca"

sys.path.append(scriptdir)
sys.path.append(hcadir)

from collections import Counter

EOD_line='---END.OF.DOCUMENT---'

letter_re = re.compile(r'\w')
def lowermatch(x):
    return x.group(0).lower()
def uppermatch(x):
    return x.group(0).upper()

def downcase_word_first(s, lowers={}, uppers={}):
    l = letter_re.sub(lowermatch, s)
    return l if l in lowers and letter_re.sub(uppermatch, s) != s else s

def downcase_sentence_first(s, lowers={}, uppers={}):
    words = s.split()
    if len(words):
        words[0] = downcase_word_first(words[0], lowers, uppers)
    return ' '.join(words)

def docline(line, downcase_first=True, tokenize=True, lowers={}, uppers={}):
    if isinstance(line, list):
        if len(line) > 0:
            line[0] = downcase_sentence_first(line[0], lowers, uppers)
        return line
    line = _native_to_unicode(line)
    line = singlespace(line)
    if downcase_first:
        line = downcase_sentence_first(line)
    return tokenizer.encode(line) if tokenize else line.split()

def docs(input, downcase_first=True, tokenize=True, eod=EOD_line, lowers={}, uppers={}):
    tok = []
    for line in input:
        line = chomp(line)
        if line == eod:
            yield tok
            tok = []
        tok += docline(line, downcase_first, tokenize, lowers, uppers)
    if len(tok):
        yield tok

def tokens(input, downcase_first=True, tokenize=True, eod=EOD_line):
    d = None
    for doc in docs(input, tokenize, eod):
        assert d is None
        d = doc
    return d

re.UNICODE = True
nonalphare = re.compile(r'[\W\d_]')

def allow_word(w, opt, stopwords):
    alpha = opt.allow_nonalpha or nonalphare.search(w) is None
    nonstop = stopwords is None or (w if opt.cased_stopwords else w.lower()) not in stopwords
    n = ustrlen(w)
    return alpha and nonstop and n >= opt.min_chars and n <= opt.max_chars


class Vocab(object):
    """word id = line number in vocab.txt file (i.e. no word '0')
    """
    def __init__(self):
        self.words = [None]
        self.ids = {}

    def id(self, w):
        if w in self.ids:
            return self.ids[w]
        else:
            self.words.append(w)
            n = len(self.words)
            self.ids[w] = n
            return n

    def str(self, id):
        if not isinstance(id, int):
            return id
        assert id > 0
        return self.words[id]

    def write(self, out):
        for i in range(1, len(self.words)):
            out.write(self.words[i]+"\n")

    def maxid(self):
        return len(self.words) - 1

class Doc(object):
    """tokens in a doc
    """
    def __init__(self, opt, name, id, tokens=None, stopwords={}):
        self.name = '%s.%s' % (id, name)
        self.id = id
        self.opt = opt
        self.vocab = opt.vocab
        self.tokens = [] if tokens is None else tokens
        self.stopwords = stopwords
        self.__wordbag = None

    def wordbag(self):
        """filtered bag (multiset) of tokens using vocab"""
        newstop = False
        opt = self.opt
        vocab = self.vocab
        if self.__wordbag is None:
            wb = Counter()
            for w in self.tokens:
                if allow_word(w, opt, self.stopwords):
                    wb[w if vocab is None else vocab.id(w)] += 1
            self.__wordbag = wb
        return self.__wordbag

    def ncounts(self):
        return len(self.wordbag())

    def wordbag_ldac_str(self):
        wb = self.wordbag()
        return ' '.join(['%s:%s' % (k, wb[k]) for k in wb])

    def wordbag_txtbag_str(self):
        wb = self.wordbag()
        return ' '.join(['%s %s' % (k - 1, wb[k]) for k in sorted(wb)])

    def out_ldac(self, out):
        out.write("%s %s\n" % (self.name, self.wordbag_ldac_str()))

    def out_txtbag(self, out):
        out.write("%s %s\n" % (self.id, self.wordbag_txtbag_str()))

    def out_docword(self, out):
        wb = self.wordbag()
        for k in sorted(wb):
            out.write("%s %s %s\n" % (self.id, k - 1, wb[k]))

    def __str__(self):
        return '%s: %s' % (self.name, self.wordbag().most_common(10))

    def ngrams(self, n=2):
        t = self.tokens
        for i in range(0, len(t) - 2):
            yield tuple(t[i:i + n])

def read_docs(doclist, stopwords, opt, id, eod=EOD_line, name=None):
    lowers = Counter()
    uppers = Counter()
    if opt.sentences:
        count_mixed(doclist, lowers, uppers, eod)
    if name is None:
       name = '' if isinstance(docs, list) else docs
    docseq = docs(doclist if isinstance(doclist, list)
                      else open(doclist), tokenize=opt.tokenize, downcase_first=opt.sentences, eod=eod)
    for toks in docseq:
        yield Doc(opt, name, id, toks, stopwords)
        id += 1

def read_docs_list(doclist, stopwords, opt, id, eod=EOD_line, name=None):
    if isinstance(doclist, list):
        for lines in doclist:
            for doc in read_docs(lines, stopwords, opt, id, eod, name):
                yield doc
                id += 1
    else:
        read_docs_list([doclist], stopwords, opt, id, eod, name)

def count_mixed(doclist, lowers=None, uppers=None, eod=EOD_line):
    if isinstance(doclist, list):
        for doc in doclist:
            for line in (doc if isinstance(doc, list) else opengz(doc)):
                line = chomp(line)
                if line == eod:
                    continue
                for word in line.split():
                    lower = letter_re.sub(lowermatch, word)
                    if lower == word and lowers is not None:
                        lowers[lower] += 1
                    upper = letter_re.sub(uppermatch, word)
                    if upper == word and uppers is not None:
                        uppers[upper] += 1
    else:
        count_mixed([doclist], lowers, uppers, eod)

def withvocab(opt):
    if not hasattr(opt, "vocab"):
       opt.vocab = Vocab()
    return opt

class Docset(object):
    """Doc objects from list of docs (from filename(s) or list of list of sentences).
    """
    def __init__(self, opt, docs=None, stopwords=None):
        self.docs = []
        self.__vocab = withvocab(opt).vocab
        if stopwords is None:
            try:
                stopwords = tokens(open(fileSCRIPTDIR(opt.stopwords)), tokenize=False, downcase_first=False)
                log("stopwords: %s ..."%' '.join(stopwords[:10]), 2)
            except IOError:
                log("stopwords file %s not found. no stopwords"%sw, 0)
        if docs is None:
            docs = opt.docs
        self.stopwords = frozenset(stopwords)
        self.opt = opt
        self.load(docs)

    def ngrams(self, n=2, topicindex=-1):
        """TODO: restrict to ngrams labeled by given topicindex if >= 0"""
        for doc in self.docs:
            for ng in doc.ngrams(n):
                yield ng

    def bagngrams(self, n=2, topicindex=-1):
        ngrams = Counter()
        for ng in self.ngrams(n, topicindex):
            ngrams[ng] += 1
        log('Docset %s-grams: %s ...'%(n, ngrams.most_common(20)), 2)
        return ngrams

    def add(self, doc):
        self.docs.append(doc)

    def load(self, docfile):
        for doc in read_docs_list(docfile, self.stopwords, self.opt, len(self.docs) + 1):
            self.add(doc)

    def out_ldac(self, out):
        '''first word added gets index 1
        '''
        for doc in self.docs:
            doc.out_ldac(out)

    def vocab(self):
        for doc in self.docs:
            doc.wordbag()
        return self.__vocab

    def out_txtbag(self, out):
        '''first word added gets index 0
        '''
        out.write('%s\n%s\n'%(len(self.docs), self.vocab().maxid()))
        for doc in self.docs:
            doc.out_txtbag(out)

    def out_docword(self, out):
        header = '%s\n%s\n%s\n'%(len(self.docs), self.vocab().maxid(), self.ncounts())
        out.write(header)
        for doc in self.docs:
            doc.out_docword(out)

    def out_docword_vocab_files(self, stem):
        indir = os.path.dirname(stem)
        stem = os.path.basename(stem)
        df = os.path.join(indir, 'docword.%s.txt' % stem)
        vf = os.path.join(indir, 'vocab.%s.txt' % stem)
        self.vocab().write(opengz(vf, 'w'))
        self.out_docword(opengz(df, 'w'))

    def ncounts(self):
        n = 0
        for d in self.docs:
            n += d.ncounts()
        return n

    def __str__(self):
        sep='\n '
        return '%s docs:%s%s' % (len(self.docs), sep, sep.join(map(str, self.docs)))


def TopicDiscovery_defaults():
    return options().parse_args([])

import subprocess

def stderr_from_cmd(cmd, logging=False, **kw):
    proc = subprocess.Popen(cmd, shell=False, stderr=subprocess.PIPE, **kw)
    lines = []
    logrc = logging
    if global_logging < 2:
        logging = False
    for line in proc.stderr:
        if logging:
            log(chomp(line), 2)
        lines.append(line)
    rc = proc.wait()
    if logrc:
        log('rc=%s %s' % (rc, ' '.join(cmd)), 1)
    if rc != 0 and not logging:
        log("ERROR EXIT %s. STDERR:" % rc)
        for line in lines:
            log(chomp(line))
    return lines

def hca_topics_args(opt):
    iters = opt.quality * 50
    opts = [opt.hca_bin, '-q8', '-v', '-v', '-v', '-e', '-C%s'%iters, '-K%s'%opt.classes]
    if opt.hca_burst:
        opts += ['-Sbdk=100', '-Sad=%s'%opt.hca_burst]
    out = 'c%s.%s.b%s' % (opt.classes, opt.stem, opt.hca_burst)
    opts += [opt.stem, out]
    return opts

def hca_topicwords_args(opt):
    rank = opt.hca_rank
    opts = [opt.hca_bin, '-q8', '-v', '-v', '-V', '-r0', '-C0', '-o%s,%s'%(opt.hca_rank, opt.name_length), '-e']
    out = 'c%s.%s.b%s' % (opt.classes, opt.stem, opt.hca_burst)
    opts += [opt.stem, out]
    return opts

topicre = re.compile(r'topic (\d+)\/\d+ words=(.*)')

class Topic(object):
    def __init__(self, opt, id):
        self.opt = opt
        self.id = id
        self.words = []
        self.vocab = opt.vocab

    def prepend_truncate(self, l):
        self.words = l + self.words
        self.truncate()

    def truncate(self):
        self.words = self.words[0:self.opt.topic_length]
        removes = {}
        for ngram in self.words:
            words = ngram.split()
            if len(words) > 1:
                for w in words:
                    removes[w] = 1
        if len(removes):
            self.words = [w for w in self.words if w not in removes]

    def __str__(self):
        words = [self.vocab.str(w) for w in self.words]
        return ', '.join(words)

    def assign(self, words):
        self.words = [to_unicode(w) for w in words]

    def __len__(self):
        return len(self.words)

class TopicDiscovery(object):
    def __init__(self, opt, docset=None, recompute_topics=True):
        global global_logging_once
        if opt.verbose > global_logging_once:
            global_logging_once = opt.verbose
        self.opt = withvocab(opt)
        self.topics = []
        for i in range(self.opt.classes):
            self.topics.append(Topic(self.opt, i))
        self.have_topics = False
        self.have_ngram_topics = False
        ds = Docset(opt, docs=opt.docs) if docset is None else docset
        self.docset = ds
        if recompute_topics:
            ds.out_docword_vocab_files(opt.stem)
            stderr_from_cmd(['%s/docword2bag.pl' % scriptdir, opt.stem], logging=False)
            stderr_from_cmd(['%s/txt2lda.pl' % scriptdir, opt.stem, opt.stem], logging=False)
            cmd = hca_topics_args(opt)
            stderr_from_cmd(cmd, logging=False)

    def topicwords(self):
        if self.have_topics:
            return self.topics
        self.have_topics = True
        for l in stderr_from_cmd(hca_topicwords_args(self.opt)):
            self.parse_assign(l)
            log(l, 2)
        return self.topics

    def ngram_topics(self, n=2):
        topics = self.topicwords()
        ngrams = self.docset.bagngrams(n)
        if n == 1:
            return
        assert n == 2
        topiclist = []
        for topic in topics:
            words = topic.words
            topicn = []
            for i in range(len(words)):
                for j in range(i + 1, len(words)):
                    ngram = (words[i], words[j])
                    if ngram in ngrams:
                        ngt = ' '.join(ngram)
                        topicn.append(ngt)
                        log("%s-gram %s"%(n, ngt))
            topiclist.append(topicn)
        return topiclist

    def topicphrases(self):
        if self.have_ngram_topics:
            return self.topics
        self.have_ngram_topics = True
        ntopics = self.ngram_topics(2)
        topics = self.topics
        ts = self.topics
        for i in range(len(ts)):
            ts[i].prepend_truncate(ntopics[i])
        return self.topics

    def parse_assign(self, topicline):
        m = topicre.match(to_unicode(topicline))
        if m is not None:
            topic = int(m.group(1))
            assert topic < len(self.topics)
            self.topics[topic].assign(m.group(2).split(','))

    def __str__(self):
        self.topicphrases()
        return '\n'.join(str(topic) for topic in self.topics) + '\n'

    def outfile(self, x, ext):
        return "%s.%s.%s"%(x, self.opt. stem,ext)


def main(opt):
    td = TopicDiscovery(opt)
    topics = td.topicphrases()
    print(str(td))

if __name__ == '__main__':
    try:
        opt = options().parse_args()
        main(opt)
    except KeyboardInterrupt:
        log("^C user interrupt", 0)
