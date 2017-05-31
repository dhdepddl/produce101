# -*- coding: utf-8 -*-
def count_word_in_topic(doc, words):
    cnt = 0
    for noun in doc:
        for word in words:
            if noun == word:
                cnt += 1
    return cnt

def rating_doc(doc, topic_set):
    rst_topics = []
    tp_len = len(topic_set)
    for i in range(tp_len):
        rst_topics.append(0)

    sum = 0
    for i in range(tp_len):
        word_cnt = count_word_in_topic(doc, topic_set[i])
        rst_topics[i] += word_cnt
        sum += word_cnt

    return rst_topics


class Post:
    topic = []

    def __init__(self, postId, user, text):
        import os
        self.user = user
        self.postId = postId
        self.text = text
        self.topic = []
        if os.name == 'posix' or 'mac':
            from konlpy.tag import Mecab
            self.noun_set = Mecab().nouns(text)
        else:
            from konlpy.tag import Twitter
            self.noun_set = Twitter().nouns(text)

    def get_topic(self, topic_set, numOftopic):
        try:
            cnt_list = rating_doc(self.noun_set, [x.words for x in topic_set])
        except AttributeError as e:
            print (str(e) + '. first parameter must be a list of Topic class instance')
        else:
            self.topic = []
            topic_cnts = cnt_list[:]
            topic_cnts.sort()
            topic_cnts.reverse()
            topNval = topic_cnts[:numOftopic]
            for i in range(numOftopic):
                self.topic.append({'topic': cnt_list.index(topNval[i]), 'count': topNval[i]})
                cnt_list[cnt_list.index(topNval[i])] = 0

    def printpost(self):
        user = self.user
        if self.user is None: user = u''
        text = self.text
        if self.text is None: text = u''
        top = [str(x['topic']) for x in self.topic]
        print u'user: ' + user + u'\ntext: ' + text + u'\ntopic: ' + u', '.join(top).encode('utf-8').strip()

    def json(self):
        import json
        return json.dumps({"user": self.user, "text": self.text, "topic": self.topic})


if __name__ == '__main__':
    # import io
    # from konlpy.utils import pprint
    # topic = []
    # f = io.open('../cf/topic', 'r', encoding='utf8')
    # while True:
    #     line = f.readline()
    #     if not line: break
    #     nouns = line.split(' ')
    #     nouns.pop(0)
    #     topic.append(nouns)
    # test_post = Post(0, u'dhdepddl', u'나 단거먹고싶어 마카롱먹을까 초코렛먹을까 마카롱 초콜렛')
    # test_post.get_topic(topic, 3)
    # test_post.printpost()
    # for i in range(len(test_post.noun_set)):
    #     pprint(test_post.noun_set[i])

    import Topic
    import io

    tm = Topic.TopicManager()

    f = io.open('dummy_data', 'r', encoding='utf8')
    cnt = 0
    post_id = u''
    text = u''
    choice1 = u''
    choice2 = u''
    for line in f:
        line = line.replace(u'\n', u'')
        if cnt%4 == 0:
            post_id = line
        elif cnt%4 == 1:
            text = line
        elif cnt%4 == 2:
            choice1 = line
        else:
            choice2 = line
            new_post = Post(post_id, u'12345678', text+u' '+choice1+u' '+choice2)
            tm.add_post(new_post)
            print(new_post.noun_set)
            new_post.printpost()
        cnt += 1
    tm.get_topic_from_posts(20, 8)
    test_post = Post(0, u'dhdepddl', u'나 단거먹고싶어 마카롱먹을까 초코렛먹을까 마카롱 초콜렛')
    print tm.topic_set
    test_post.get_topic(tm.topic_set, 3)
    print test_post.topic

