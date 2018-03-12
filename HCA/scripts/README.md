Download:
git clone https://github.com/graehl/topic-models.git

Build (needs C++11 for threads):
cd topic-models && make -j8

Run (one or more docs per file):
cd HCA/scripts && python ./topics.py /home/graehl/ql/wp.1000.txt ./README.txt -k 5 -l 10

Awards ceremony, film awards, awards ceremony, Lincoln, Oscar, Illinois, Hollywood, Grant, Party
Algerian Arabic, Aristotle, Algeria, Algiers, Plato, logic, Berber, Algerians, Africa
Alabama counties, rural counties, anarchism, anarchists, anarchist, Birmingham, individualist, Mobile, Gershwin
Achilles, albedo, Hector, Thetis, Trojan, Patroclus, Troy, Odysseus, Iliad, reflectance
ASD symptoms, autistic symptoms, autistic behavior, Rand, autism, altruism, TAI, genetic, syndrome

(input file:
…
The diversity in anarchism has led to widely different use of identical terms among different anarchist traditions ,  which has led to many definitional concerns in anarchist theory .
---END.OF.DOCUMENT---
Autism is a disorder of neural development characterized by impaired social interaction and communication ,  and by restricted and repetitive behavior .
…)

API usage:

import topics as T

topt = T.TopicDiscovery_defaults()
topt.topics = 10
topt.topic_length = 12
topt.sentences = True
topt.docs = []
topt.docs.append('topics-demo.py') # reads text from file
topt.docs.append(['A very tall oak tree.', 'The next sentence is about France.'])
topt.docs.append([['List', 'of', 'tokens', 'in', 'a', 'sentence', '.'], 'Another sentence!'])
topt.docs.append(["Two documents\n---END.OF.DOCUMENT---\nSecond document"])

td = T.TopicDiscovery(topt)
topics = td.topicphrases() # returns list of Topic object. Topic objects are printable
print str(td) # pretty-prints topicphrases()

(see also several other scripts in README.txt)
