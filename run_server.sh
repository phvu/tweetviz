#!/usr/bin/env bash

# couchdb &

# curl -X GET http://127.0.0.1:5984/_all_dbs
# curl -X DELETE http://127.0.0.1:5984/tweetviz

THEANO_FLAGS=floatX=float32,device=gpu0 python tweetviz_server.py