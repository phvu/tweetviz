import tempfile
import os
import numpy as np
from twitter import Twitter, OAuth, TwitterHTTPError
import conf
from skip_thoughts import skipthoughts
from skip_thoughts.bh_tsne import bhtsne


def remove_unicode(ss):
    s2 = []
    for s in ss:
        s = s.split(' ')
        s = [x for x in s if all(ord(c) < 128 for c in x)]
        if len(s) > 0:
            s2.append(' '.join(s))
    return s2


def run_tsne(vecs):
    with tempfile.NamedTemporaryFile('w', delete=False) as f_in:
        np.savetxt(f_in.name, vecs, delimiter='\t')
        in_file = f_in.name
    with tempfile.NamedTemporaryFile('w', delete=False) as f_out:
        out_file = f_out.name

    perplexity = 30.0
    while True:
        try:
            bhtsne.main(['bhtsne.py', '-d', '3', '-p', '{}'.format(perplexity), '-v', '-i', in_file, '-o', out_file])
            break
        except AssertionError as ex:
            print('Error with bh_tsne: ', ex)
            perplexity *= 0.9
            if perplexity < 0.1:
                raise RuntimeError('Unable to compute t-SNE for this user with a sensible perplexity')
            print('Trying again with perplexity = {}'.format(perplexity))

    vectors = np.loadtxt(out_file, delimiter='\t')

    for s in [in_file, out_file]:
        try:
            os.remove(s)
        except IOError:
            pass
    return vectors


class TweetFetcher(object):

    def __init__(self, with_skipthought=True):
        self.twitter = Twitter(auth=OAuth(conf.twitter_access_key,
                                          conf.twitter_access_secret,
                                          conf.twitter_consumer_key,
                                          conf.twitter_consumer_secret))
        if with_skipthought:
            self.skipthought_model = skipthoughts.load_model()
        print('Done initializing TweetFetcher')

    def get_tweets(self, username):
        try:
            ls = self.twitter.statuses.user_timeline(screen_name=username, include_rts=1, count=conf.MAX_TWEETS)
            return [{'text': s['text'], 'id': s['id_str']} for s in ls]
        except (TwitterHTTPError, ValueError):
            raise RuntimeError('Requesting tweets failed for user {}'.format(username))

    def tweets_to_vec(self, tweets):
        filtered_tweets = []
        for item in tweets:
            t = skipthoughts.preprocess(remove_unicode([item['text']]))
            if len(t) == 1 and len(t[0]) > 0:
                filtered_tweets.append({'text': t[0], 'id': item['id']})

        if len(filtered_tweets) < 3:
            raise RuntimeError('This user has too few valid tweets ({}). '
                               'We need at least 3.'.format(len(filtered_tweets)))

        vecs = skipthoughts.encode(self.skipthought_model, [s['text'] for s in filtered_tweets]).astype(np.float64)
        vecs = run_tsne(vecs)

        return filtered_tweets, vecs

    def fetch(self, username):
        tweets = self.get_tweets(username)
        tweets, vecs = self.tweets_to_vec(tweets)

        assert vecs.shape[1] == 3 and vecs.shape[0] == len(tweets)
        pt = []
        for i, s in enumerate(tweets):
            pt.append({'x': vecs[i, 0], 'y': vecs[i, 1], 'z': vecs[i, 2], 'tweet': s['text'], 'id': s['id']})
        return pt
