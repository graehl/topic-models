import topics as T

topt = T.TopicDiscovery_defaults()
topt.topics = 10
topt.topic_length = 12
topt.sentences = True
topt.docs = []
topt.docs.append('topics-demo.py') # reads text from file
#TODO: debug - supposed to allow input of docs, sentences, tokens *not* from file
#topt.docs.append(['A very tall oak tree.', 'The next sentence is about France.'])
#topt.docs.append([['List', 'of', 'tokens', 'in', 'a', 'sentence', '.'], 'Another sentence!'])
#topt.docs.append(["Two documents\n---END.OF.DOCUMENT---\nSecond document"])

td = T.TopicDiscovery(topt)
topics = td.topicphrases() # returns list of Topic object. Topic objects are printable
print str(td) # prints topicphrases
