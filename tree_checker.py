#!/usr/bin/env python3

import six
assert six.PY3, "Run me with python3"

from flask import Flask, Markup
import flask
import json
import requests
import traceback

DEBUGMODE=False
try:
    from config_local import * #use to override the constants above if you like
except ImportError:
    pass #no config_local

app = Flask("checker")

@app.route("/set",methods=["POST"])
def post():
    
    



@app.route("/save",methods=[u"POST"])
def query_save():
    pass
    # try:
    #     q=Query.from_formdata(flask.request.form)
    #     r=requests.get(DEP_SEARCH_WEBAPI,params={u"db":q.treeset, u"case":q.case_sensitive, u"context":3, u"search":q.query, u"retmax":q.hits_per_page})
    #     if r.text.startswith(u"# Error in query"):
    #         ret = flask.render_template(u"query_error.html", err=r.text)
    #     elif not r.text.strip():
    #         ret = flask.render_template(u"empty_result.html")
    #     else:
    #         ret=flask.render_template(u"result_tbl.html",trees=yield_trees(r.text.splitlines()))

    #     return json.dumps({u'ret':ret,u'query_link':q.query_link(),u'download_link':q.download_link()});
    # except:
    #     traceback.print_exc()
        

if __name__ == u'__main__':
    app.run(debug=DEBUGMODE)
    r=requests.get(DEP_SEARCH_WEBAPI+u"/metadata") #Ask about the available corpora
    metadata=json.loads(r.text)

