class Topic:
    def __init__(self, topic_id, words):
        self.topic_id = topic_id
        self.words = words


class TopicManager:
    def __init__(self):
        self.topic_set = []
        self.post_set = []

    def reset_topics(self):
        self.topic_set = []

    def reset_posts(self):
        self.post_set = []

    def add_post(self, new_post):
        if new_post.__class__.__name__ == 'Post':
            self.post_set.append(new_post)
        else:
            raise TypeError('input parameter is not Post class')

    def get_topic_from_posts(self, X, vocabs, num_of_words, num_of_topics, alpha=0.02, eta=0.005):
        import lda_module as lda
        import numpy
        model = lda.LDA(n_topics=num_of_topics, n_iter=1000, random_state=1, alpha=alpha, eta=eta)
        model.fit(X)
        topic_word = model.topic_word_
        for i, topic_dist in enumerate(topic_word):
            try:
                topic_words = numpy.array(vocabs)[numpy.argsort(topic_dist)][:-(num_of_words + 1):-1]
            except IndexError as e:
                print (str(e))
            else:
                new_topic = Topic(i, topic_words)
                self.topic_set.append(new_topic)

    def get_topic_from_file(self, path, numOfwords):
        import io
        try:
            f = io.open(path, 'r', encoding='utf8')
        except IOError as e:
            print(str(e))
        else:
            while True:
                line = f.readline()
                if not line: break
                nouns = line.split(' ')
                id = int(nouns.pop(0))
                if numOfwords >= len(nouns):
                    print 'number of words is larger than words in topic_set'
                    numOfwords = len(nouns)-1
                words = nouns[:numOfwords]
                self.topic_set.append(Topic(id, words))

    def write_topic_set(self, path):
        import io
        f = io.open(path, 'w', encoding='utf8')
        for topic in self.topic_set:
            f.write(str(topic.topic_id).encode('utf8') + u' ')
            for word in topic.words:
                f.write(word + u' ')
            f.write(u'\n')
