#!/usr/bin/env bash

git clone https://github.com/phvu/skip-thoughts.git ./skip_thoughts/
cd ./skip_thoughts/
./setup.sh
cd ../

if [ ! -f ./conf.py ]; then
    cp ./conf.templates.py ./conf.py
fi
echo "Done."