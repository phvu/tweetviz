# tweetviz
Tweet visualization

Basically you will need to install Theano (and CUDA if you want to use GPUs), then go:

    pip install -r requirements.txt
    ./setup.sh

Install and start `couchdb` on your system.

Then update the configuration parameters in `conf.py`, and start the server with:
        
    ./run_server.sh
