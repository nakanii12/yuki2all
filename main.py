import json
import requests
import time

webhook = r"https://discord.com/api/webhooks/955012567762362368/oPQg-L6Zl78QTTP0lALkF3Yn9iJIa4AmQNdoxtmDwI1LbPgng70k_u4xys2141CSRkkb"
def post_log(log):
    global webhook
    requests.post(webhook,{"content": log})

def get_data(videoid):
    post_log(fr"https://youtube.com/watch?v={videoid}")
    t = json.loads(requests.get(r"https://vid.puffyan.us/api/v1/videos/"+ videoid).text)
    return [{"id":i["videoId"],"title":i["title"],"authorId":i["authorId"],"author":i["author"]} for i in t["recommendedVideos"]],t["formatStreams"][-1]["url"],t["descriptionHtml"].replace("\n","<br>"),t["title"]

def get_search(q,page):
    post_log(fr"https://youtube.com/search?q={q}")
    t = json.loads(requests.get(r"https://vid.puffyan.us/api/v1/search?q="+ q + "&page=" + page).text)
    return [{"title":i["title"],"id":i["videoId"],"authorId":i["authorId"],"author":i["author"]} for i in t]

def get_channel(channelid):
    post_log(fr"https://youtube.com/channel/{channelid}")
    t = json.loads(requests.get(r"https://vid.puffyan.us/api/v1/channels/"+ channelid).text)["latestVideos"]
    return [{"title":i["title"],"id":i["videoId"],"authorId":i["authorId"],"author":i["author"]} for i in t]

from flask import Flask,render_template,request,abort,make_response,redirect

def check_cokie():
    if request.cookies.get('yuki', None) == "True":
        return True
    return False
    
app = Flask(__name__, static_folder='./static', static_url_path='')
@app.route("/")
def home():
    if check_cokie():
        return render_template("home.html")
    return """<head><title>連番を簡単に生成！！</title></head><body><form action="/answer" method="get">
    <input type="text" name="q" required>
    <input type="submit" value="生成！！">
</form></body>"""

@app.route('/watch')
def video():
    if not(check_cokie()):
        return abort(404)
    videoid = request.args.get("v")
    t = get_data(videoid)
    response = make_response(render_template('video.html',videoid=videoid,videourl=t[1],res=t[0],description=t[2],videotitle=t[3]))
    response.set_cookie("yuki",value="True",expires=time.time() + 60 * 60 * 24 * 7)
    return response

@app.route("/search")
def search():
    if not(check_cokie()):
        return abort(404)
    q = request.args.get("q")
    page = str(int(request.args.get("page","0")) + 1)
    response = make_response(render_template("search.html",results=get_search(q,page),word=q,next=f"/search?q={q}&page={page}"))
    response.set_cookie("yuki",value="True",expires=time.time() + 60 * 60 * 24 * 7)
    return response

@app.route("/channel/<channelid>")
def channel(channelid):
    if not(check_cokie()):
        return abort(404)
    response = make_response(render_template("search.html",results=get_channel(channelid),word="",next=f"/channel/{channelid}"))
    response.set_cookie("yuki",value="True",expires=time.time() + 60 * 60 * 24 * 7)
    return response

@app.route("/answer")
def set_cokie():
    q = request.args.get("q")
    response = make_response("<head><title>連番を簡単に生成！！</title></head><body>"+" ".join([str(i) for i in range(int(q))])+"</body>")
    if q == "090328":
        response.set_cookie("yuki",value="True",expires=time.time() + 60 * 60 * 24 * 7)
        response.headers['Location'] = '/'
    return response,302

@app.errorhandler(404)
def page_not_found(error):
    return """<head><title>連番を簡単に生成！！</title></head><body><form action="/answer" method="get">
    <input type="text" name="q" required>
    <input type="submit" value="生成！！">
</form></body>"""
