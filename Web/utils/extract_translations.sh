#!/usr/bin/bash
version=`cat setup.py | grep "version" | sed "s/[]*, version[]*= //" | sed "s/'//g"`
pybabel extract --mapping=babel.map --output=httpca_web/translations/en.pot --msgid-bugs-address="puiterwijk@gmail.com" --copyright-holder="Patrick Uiterwijk" --project="HttpCA" --version="$version" httpca_web/
