import io
import lda
import numpy
import time
import os
from Post import Post


# part1. open file and parse
# If userId is not None, get only the user's post
def get_user_post(path, userId=None):
    f = io.open(path, 'r', encoding='utf8')

    user_contents = []
    twit_list = []
    nickname = u""
    twit = u""
    UID = u""

    if userId is not None:
        UID = userId
        for line in f:
            if (line[:4] == u"ID: ") and (
                line.replace(u"ID: ", u"")[:-1] == userId): break  # find the line where userId is

    for line in f:
        if line[:4] == u"ID: ":
            if userId is None:
                UID = line.replace(u"ID: ", u"")[:-1]
                continue
            else:
                break

        else:
            twit_list = line.split("\t|\t")
            nickname = twit_list[0]
            twit = "\t|\t".join(twit_list[1:])
            user_contents.append({"id": UID, "nick": nickname, "tweet": twit})

    return user_contents


def get_post(path, userId=None):
    f = io.open(path, 'r', encoding='utf8')

    user_contents = []
    twit_list = []
    nickname = u""
    twit = u""
    UID = u""

    if userId is not None:
        UID = userId
        for line in f:
            if (line[:4] == u"ID: ") and (
                line.replace(u"ID: ", u"")[:-1] == userId): break  # find the line where userId is
    linecnt = 0
    for line in f:
    ## to reduce test time
    # for i in range(100):
    #     line = f.readline()
    ## to reduce test time
        linecnt += 1
        if line[:4] == u"ID: ":
            if userId is None:
                UID = line.replace(u"ID: ", u"")[:-1]
                continue
            else:
                break
        else:
            twit_list = line.split("\t|\t")
            nickname = twit_list[0]
            twit = "\t|\t".join(twit_list[1:])
            user_contents.append(Post(linecnt, UID, twit))
    return user_contents


# If nick is not None, get only the user's post
def get_user_post_nick(path, nick=None):
    f = io.open(path, 'r', encoding='utf8')

    user_contents = []
    twit_list = []
    nickname = u""
    twit = u""
    nick_found = False
    UID = u""

    for line in f:
        if line[:4] == u"ID: ":
            UID = line.replace(u"ID: ", u"")[:-1]
            if nick_found:
                break
            elif nick is None:
                continue
        else:
            twit_list = line.split("\t|\t")
            nickname = twit_list[0]
            twit = "\t|\t".join(twit_list[1:])
            if nick is not None:
                if nickname == nick:
                    nick_found = True
                else:
                    continue

            user_contents.append({"id": UID, "nick": nickname, "tweet": twit})
            print UID + " : " + nickname + " + " + twit

    return user_contents


# part2. use konlpy to parse documents
def make_noun_set(content):
    from konlpy.tag import Twitter
    parser = Twitter()
    if os.name == 'mac' or 'posix':
        from konlpy.tag import Mecab
        parser = Mecab()
    docs = []
    nounset = []
    for doc in content:
        nouns = parser.nouns(doc['tweet'])
        nounset += nouns
        docs.append(nouns)
    nounset = list(set(nounset))
    rst = []
    for noun in nounset:
        if len(noun) > 1:
            rst.append(noun)
    return docs, rst


# part3. make input matrix
def matrix_lda(docs, nouns):
    len_docs = len(docs)
    len_nouns = len(nouns)
    X = numpy.zeros(shape=(len_docs, len_nouns), dtype=int)
    for j in range(len_docs):
        doc = docs[j]
        for i in range(len_nouns):
            noun = nouns[i]
            cnt = doc.count(noun)
            X[j][i] = cnt

    return X


# part4. lda
def exec_lda(mtx_lda, vocab_set, topics, words, iterations, path='./topic'):
    import numpy
    ft = io.open(path, 'w', encoding='utf8')
    model = lda.LDA(n_topics=topics, n_iter=iterations, random_state=1)
    model.fit(mtx_lda)
    topic_word = model.topic_word_
    n_top_words = words
    print topic_word
    for i, topic_dist in enumerate(topic_word):
        try:
            topic_words = numpy.array(vocab_set)[numpy.argsort(topic_dist)][:-(n_top_words + 1):-1]
        except IndexError as e:
            print (str(e))
        else:
            words = u''
            for word in topic_words:
                words += word
                words += ' '
            ft.write(str(i).encode('utf8') + u' ' + words + u'\n')


if __name__ == '__main__':
    import pyLDAvis
    start_time = time.time()

    # part1. open file and parse by ':::\n"
    contents = get_user_post('../get_data/twitter_data_learn')
    print("After part1: %s seconds" % (time.time() - start_time))

    # part2. use konlpy to parse documents
    doc_list, noun_set = make_noun_set(contents)
    print("After part2: %s seconds" % (time.time() - start_time))

    # part3. make input matrix
    X = matrix_lda(doc_list, noun_set)
    print("After part3: %s seconds" % (time.time() - start_time))

    # part4. lda
    exec_lda(X, noun_set, 30, 15, 1000)
    print("After part4: %s seconds" % (time.time() - start_time))