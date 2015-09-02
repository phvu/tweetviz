from flask import Flask, g, render_template, jsonify
import flaskext.couchdb
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from tweet_worker import TweetWorker
from rwlock import RWLock
import conf


finished_users = {}
finished_users_lock = RWLock()


def update_user_data(username, data):
    print('Got data of user {}'.format(username))
    finished_users_lock.acquire_read()
    if username not in finished_users:
        finished_users_lock.release()
        finished_users_lock.acquire_write()
        finished_users[username] = data
        print('Done putting data of user {}'.format(username))
    finished_users_lock.release()


def get_finished_user(username):
    d = None
    finished_users_lock.acquire_read()
    if username in finished_users:
        finished_users_lock.release()
        finished_users_lock.acquire_write()
        d = finished_users[username]
        del finished_users[username]
    finished_users_lock.release()
    return d


app = Flask(__name__)
app.config.from_object(conf)

worker = TweetWorker(conf.FETCHER_COUNT, update_user_data)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/viz/<username>/')
def viz(username):
    return render_template('tweets.html', username=username)


@app.route('/query/<username>')
def query(username):
    data = g.couch.get(username)
    if data is None or (data is not None and 'data' not in data):
        data = get_finished_user(username)
        if data is None:
            worker.get(username)
            return jsonify(working=True, has_error=False)
        else:
            current_data = g.couch.get(username)
            if current_data is None:
                g.couch[username] = data
            else:
                current_data.update(data)
                g.couch.save(current_data)

    if 'data' in data:
        return jsonify(working=False, has_error=False, points=data['data'])
    return jsonify(working=False, has_error=True, error=data['error'])


if __name__ == '__main__':
    manager = flaskext.couchdb.CouchDBManager()
    manager.setup(app)
    manager.sync(app)

    # Flask alone
    # app.run(host='0.0.0.0', port=conf.SERVICE_PORT, threaded=True)

    # with tonardo
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(conf.SERVICE_PORT)
    IOLoop.instance().start()
