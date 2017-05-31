import io
import lda_module as lda
import similarity as si


def content_topic(doc, topic_set):
    n_topic = []
    for i in range(len(topic_set)):
        cnt = 0
        words = topic_set[i]
        for noun in doc:
            if noun in words:
                cnt += 1
        if cnt > 1:
            n_topic.append(i)

    return n_topic


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


def rating_doc_set(doc_set, topic_set):
    rst_topics = []
    tp_len = len(topic_set)
    for i in range(tp_len):
        rst_topics.append(0)

    sum = 0
    for i in range(tp_len):
        for doc in doc_set:
            word_cnt = count_word_in_topic(doc, topic_set[i])
            rst_topics[i] += word_cnt
            sum += word_cnt
    if sum == 0:
        return rst_topics
    return rst_topics


def rating_list(userId, path, topic_set):
    user_contents = lda.get_user_post(path, userId)
    doc_user, noun = lda.make_noun_set(user_contents)
    return rating_doc_set(doc_user, topic_set)


def recommended_topic(user, numOftopic, user_mul, sim_mul):
    n_user_topic = int(numOftopic * user_mul / (user_mul+sim_mul))
    n_sim_topic = numOftopic-n_user_topic

    user_rating = user.topic_rating[:]
    user_rating.sort()
    user_rating.reverse()
    if numOftopic > len(user_rating):
        return IndexError('recommend numOftopic is larger than num of topics')
    top_n_user = user.topic_rating[:n_user_topic]
    top_n_topic_user = [{"count": x, "id": user.topic_rating.index(x)} for x in top_n_user]

    sim_topic_rating = []
    for j in range(len(user_rating)):
        sim_topic_rating.append(0)
    for i in range(len(user.similar_users)):
        for j in range(len(user_rating)):
            sim_topic_rating[j] += int(user.similar_users[i][2][j]/len(user.similar_users))

    sim_rating = sim_topic_rating[:]
    sim_rating.sort()
    sim_rating.reverse()
    top_n_sim = sim_topic_rating[:n_sim_topic]
    top_n_topic_sim = [{"count": x, "id": sim_topic_rating.index(x)} for x in top_n_sim]
    return top_n_topic_sim + top_n_topic_user


def recommended_posts(user, numOftopic, numOfpost, user_mul, sim_mul, post_by_topic):
    import random
    topNtopic = recommended_topic(user, numOftopic, user_mul, sim_mul)
    recommended_post_id = []
    try:
        t_sum = sum([x['count']+1 for x in topNtopic])
        print t_sum
    except:
        return []
    for topic in topNtopic:
        topic_id = topic['id']
        cnt = int(topic['count']*numOfpost/t_sum)+1
        post_list_per_topic = [x for x in post_by_topic[topic_id] if x[0] > 2]
        cnt = min(cnt, len(post_list_per_topic))
        while cnt > 0:
            post = random.choice(post_list_per_topic)
            pair = (post[1], post[2])
            if pair in recommended_post_id:
                continue
            else:
                recommended_post_id.append(pair)
                cnt -= 1
    return recommended_post_id[:numOfpost]