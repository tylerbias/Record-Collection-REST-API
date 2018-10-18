from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import abort
from google.appengine.ext import ndb

import mbrainz
import account_check

# Flip to 0 when testing locally
# FLip to 1 when deploying
DOMAIN_TOGGLE = 1

if DOMAIN_TOGGLE == 0:
    CURRENT_HOST = "http://localhost:8080"
else:
    CURRENT_HOST = "https://record-shelf-app.appspot.com"

# Easily toggle between accounts when testing using hardcoded access tokens
ACCOUNT_TOGGLE = 0

if ACCOUNT_TOGGLE == 1:
    ACCESS_TOKEN = "ya29.GluDBfkTEwBuyY0xE7-8wIHxgvFyVYGHxa6MjPavlUO3ttTa47cHJTArppccMN2h09OrYttsbtVVNHr9sVV6ysKeDFgXecdYDuxQO1ir3esQxdk5AnwPqtHg_lIO"
else:
    ACCESS_TOKEN = "ya29.GlyDBS-n6NxzrQQgsVZFK9N7d3DEg32gWtbja-Ao1vgLZafiOu-qLiCTTc7qO7wZ7FhWvb0NIdirv31SS7vv_Z38RFkrdiAIwB8el5n8TRUV8ZNLs-sFURqIM2tgpQ"



app = Flask(__name__)

class UserAccount(ndb.Model):
    name = ndb.StringProperty()
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    collection = ndb.JsonProperty(default={})
    description = ndb.StringProperty()
    googleID = ndb.StringProperty()
    
class Record(ndb.Model):
    title = ndb.StringProperty()
    releaseDate = ndb.StringProperty()
    artist = ndb.StringProperty()
    owner = ndb.StringProperty()
    art = ndb.StringProperty()
    

@app.route("/")
def main_page():
    access_token = request.headers.get('Authorization')
    if access_token:
        email = account_check.get_google_email(access_token)
        q = UserAccount.query(UserAccount.email == email)
        fetched = q.fetch()
        print fetched
        for x in fetched:
            username = x.username
        return  Response("<a href=\"%s/records\">Records</a><p></p><a href=\"%s/users\">Users</a><p></p>Logged in as %s" % (CURRENT_HOST, CURRENT_HOST, username))
        
    return  Response("<a href=\"%s/records\">Records</a><p></p><a href=\"%s/users\">Users</a>" % (CURRENT_HOST, CURRENT_HOST))


@app.route("/records", methods=['GET', 'POST'])
def records_URL():
    data = {}
    n = 0
    if request.method == 'POST':
        access_token = request.headers.get('Authorization')
        if access_token:
            email = account_check.get_google_email(access_token)
            q = UserAccount.query(UserAccount.email == email)
            fetched = q.fetch()
            activeUser = fetched[0]
            print activeUser.name
            jsonNew = request.json
            for key in jsonNew:
                if key not in ("Artist", "Title"):
                    return abort(403, "Invalid data")
            mbAPI = mbrainz.mb()
            mbData = mbAPI.get_data(jsonNew)
            newRecord = Record(artist=jsonNew["Artist"], title=jsonNew["Title"], releaseDate=mbData["Date"], art=mbData["Art"], owner="%s" % (activeUser.key.id()))
            newRecordKey = newRecord.put()
            data["Generated ID"] = newRecordKey.id()
            activeUser.collection[newRecordKey.id()] = "%s - %s // %s/records/%s" % (jsonNew['Artist'], jsonNew['Title'], CURRENT_HOST, newRecordKey.id())
            print activeUser.collection
            activeUser.put()
            json_resp = jsonify(data)
            return json_resp
        else:
            return "You have to be logged in to add a record."
    else:
        
        q = Record.query()
        fetched = q.fetch()
        for x in fetched:
            data[n] = {}
            data[n]["ID"] = str(x.key.id())
            data[n]["Title"] = x.title
            data[n]["Artist"] = x.artist
            data[n]["Art"] = x.art
            data[n]["Owner"] = x.owner
            data[n]["Release-Date"] = x.releaseDate
            data[n]["URL"] = "%s/records/%s" % (CURRENT_HOST, str(x.key.id()))
            data[n]["Owner"] = "%s/users/%s" % (CURRENT_HOST, x.owner)
            n = n + 1
        json_resp = jsonify(data)
        return json_resp
    
@app.route("/users", methods=['GET', 'POST'])
def users_URL():
    data = {}
    n = 0
    if request.method == 'POST':
        return "This site uses Google as a manager for its user accounts. As a result, an account cannot be created through the API. It must be handled through a front end, which does not yet exist. All user accounts are hardcoded currently."
    else:
        q = UserAccount.query()
        fetched = q.fetch()
        for x in fetched:
            data[n] = {}
            data[n]["ID"] = x.key.id()
            data[n]["URL"] = "%s/users/%s" % (CURRENT_HOST, x.key.id())
            data[n]["Name"] = x.name
            data[n]["Username"] = x.username
            data[n]["Email"] = x.email
            data[n]["Collection"] = "%s/users/%s/collection" % (CURRENT_HOST, x.key.id())
            data[n]["Description"] = x.description
            n += 1
        json_resp = jsonify(data)
        return json_resp
    
    
@app.route("/users/me", methods=['GET'])
def personal_account():
    data = {}
    access_token = request.headers.get('Authorization')
    if access_token:
        email = account_check.get_google_email(access_token)
        print email
        q = UserAccount.query(UserAccount.email == email)
        fetched = q.fetch()
        for x in fetched:
            data["ID"] = x.key.id()
            data["URL"] = "%s/users/%s" % (CURRENT_HOST, x.key.id())
            data["Name"] = x.name
            data["Username"] = x.username
            data["Email"] = x.email
            data["Collection"] = "%s/users/%s/collection" % (CURRENT_HOST, x.key.id())
            data["Description"] = x.description
        json_resp = jsonify(data)
        return json_resp
    else:
        abort(403)
        
@app.route("/users/me/username", methods=['PATCH'])
def change_username():
    jsonNew = request.json
    print 1
    for key in jsonNew:
        if key not in ("Username"):
            return abort(403, "Must specify a username")
    print 2
    access_token = request.headers.get('Authorization')
    if access_token:
        email = account_check.get_google_email(access_token)
        print 2
        print email
        q = UserAccount.query(UserAccount.email == email)
        fetched = q.fetch()
        theUser = UserAccount.get_by_id(int(fetched[0].key.id()))
        theUser.username = jsonNew["Username"]
        theUser.put()
        
        return Response("Username successfully updated.")
    else:
        abort(403, "You are not signed in.")
        


@app.route("/users/me/collection", methods=['GET'])
def personal_collection():
    data = {}
    n = 0
    access_token = request.headers.get('Authorization')
    email = account_check.get_google_email(access_token)
    q = UserAccount.query(UserAccount.email == email)
    fetched = q.fetch()
    for x in fetched:
        temp = dict(x.collection)
        for recordID in temp.keys():
            data[n] = {}
            theRecord = Record.get_by_id(int(recordID))
            data[n]["ID"] = recordID
            data[n]["Title"] = theRecord.title
            data[n]["Artist"] = theRecord.artist
            data[n]["Art"] = theRecord.art
            data[n]["Owner"] = theRecord.owner
            data[n]["Release-Date"] = theRecord.releaseDate
            data[n]["URL"] = "%s/records/%s" % (CURRENT_HOST, str(theRecord.key.id()))
            data[n]["Owner"] = "%s/users/%s" % (CURRENT_HOST, theRecord.owner)
            n = n + 1
    json_resp = jsonify(data)
    return json_resp

@app.route("/users/<user_id>", methods=['GET'])
def specific_user(user_id):
    data = {}
    theUser = UserAccount.get_by_id(int(user_id))
    if not theUser:
        return abort(404, "User not found")
    if request.method == 'DELETE':
        return 'eventually'
    
    data["ID"] = user_id
    data["URL"] = "%s/users/%s" % (CURRENT_HOST, theUser.key.id())
    data["Name"] = theUser.name
    data["Username"] = theUser.username
    data["Email"] = theUser.email
    data["Collection"] = "%s/users/%s/collection" % (CURRENT_HOST, user_id)
    data["Description"] = theUser.description
    
    json_resp = jsonify(data)
    return json_resp

@app.route("/users/<user_id>/collection", methods=['GET'])
def specific_collection(user_id):
    data = {}
    n = 0
    theUser = UserAccount.get_by_id(int(user_id))
    temp = dict(theUser.collection)
    for recordID in temp.keys():
        data[n] = {}
        theRecord = Record.get_by_id(int(recordID))
        data[n]["ID"] = recordID
        data[n]["Title"] = theRecord.title
        data[n]["Artist"] = theRecord.artist
        data[n]["Art"] = theRecord.art
        data[n]["Owner"] = theRecord.owner
        data[n]["Release-Date"] = theRecord.releaseDate
        data[n]["URL"] = "%s/records/%s" % (CURRENT_HOST, str(theRecord.key.id()))
        data[n]["Owner"] = "%s/users/%s" % (CURRENT_HOST, theRecord.owner)
        n = n + 1
    json_resp = jsonify(data)
    return json_resp

@app.route('/records/<record_id>', methods=['GET', 'DELETE'])
def specific_record(record_id):
    data = {}
    theRecord = Record.get_by_id(int(record_id))
    if not theRecord:
        return abort(404, "Record not found.")
    if request.method == 'DELETE':
        access_token = request.headers.get('Authorization')
        if access_token:
            email = account_check.get_google_email(access_token)
            q = UserAccount.query(UserAccount.email == email)
            fetched = q.fetch()
            activeUser = fetched[0]
            print activeUser.key.id()
            print theRecord.owner
            if int(activeUser.key.id()) == int(theRecord.owner): 
                temp = dict(activeUser.collection)
                temp.pop(str(theRecord.key.id()))
                activeUser.collection = temp
                activeUser.put()
                theRecord.key.delete()
                return Response("Record deleted.", mimetype="text/plain")
            else:
                return abort(403, "You are not authorized to delete this record.")

    data["ID"] = record_id
    data["Artist"] = theRecord.artist
    data["Title"] = theRecord.title
    data["Art"] = theRecord.art
    data["Release-Date"] = theRecord.releaseDate
    data["URL"] = ("%s/records/%s" % (CURRENT_HOST, record_id))
    data["Owner"] = "%s/users/%s" % (CURRENT_HOST, theRecord.owner)
    json_resp = jsonify(data)
    return json_resp

@app.route('/oauth')
def oauth():
    return "Authorization successful."


@app.route('/hardcode', methods=["POST"])
def hardcoded():
    newUser1 = UserAccount(name="OSU Account", username="biast", email="biast@oregonstate.edu", description="Hardcoded account #2.")
    newUser2 = UserAccount(name="Tyler Bias", username="tylerbias", email="tylerbias@gmail.com", description="Hardcoded account #1.")
    newUser1.put()
    newUser2.put()
    return "Success"