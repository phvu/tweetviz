import Queue as ThreadQueue
from threading import Thread
import time
from rwlock import RWLock
from tweet_fetcher import TweetFetcher

job_queue = ThreadQueue.Queue()


class Result(object):
    def __init__(self, username, success, err, data):
        self.username = username
        self.success = success
        self.err = err
        self.data = data


def worker(jobs, results):

    fetcher = TweetFetcher()

    while True:
        username = jobs.get(block=True)

        if username is None:
            break

        try:
            pt = fetcher.fetch(username)
            results.put(Result(username, True, None, pt))
        except RuntimeError as err:
            print('Error when fetching tweets for user {}'.format(username))
            print(err)
            results.put(Result(username, False, err.message, None))

        time.sleep(1)

    # 'poison' the next worker
    jobs.put(None)


def consumer_process(results, callback):
    while True:
        r = results.get()
        if r is None:
            continue

        if r.success:
            obj = {'data': r.data}
        else:
            obj = {'error': r.err}
        callback(r.username, obj)


class TweetWorker(object):

    def __init__(self, n, callback):
        self.processing_users = []
        self.lock = RWLock()
        self.jobs = ThreadQueue.Queue()
        self.results = ThreadQueue.Queue()
        self.processes = []
        for _ in range(0, n):
            s = Thread(target=worker, args=(job_queue, self.results))
            self.processes.append(s)
            s.daemon = True
            s.start()
        print('Started {} worker processes'.format(len(self.processes)))

        self.consumer = Thread(target=consumer_process, args=(self.results, callback))
        self.consumer.daemon = True
        self.consumer.start()
        print('Started consumer process')

    def get(self, username):
        if username is None:
            return

        self.lock.acquire_read()
        if username in self.processing_users:
            self.lock.release()
            return
        self.lock.release()

        self.lock.acquire_write()
        self.processing_users.append(username)
        self.lock.release()
        job_queue.put(username)
        return
