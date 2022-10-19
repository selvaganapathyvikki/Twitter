
import cherrypy
import os, os.path
from datetime import datetime
from credentials import get_jwt_token, encrypt_password, check_password
from db import connection
from activities import getTweets, getTweetsById, getAccountsList, get_sql_command_for_activity, \
    get_user_handle_using_token, get_sql_command_for_location, get_sql_command_for_action, \
    validate_follow_request, validate_tweet_activities, getLikesInfo, getRetweetsInfo, getRepliesInfo
from trends import getTrends
import user
import tweets
import cherrypy_cors
cherrypy_cors.install()


class Twitter(object):

    def __init__(self):
        self.conn = connection()
        self.cursor = self.conn.cursor()


    #sign up route
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sign_up(self, account_name="", first_name="", last_name="", email="", password="", phone_number=0, is_private_account="", location="") :

        #handling is_private_account
        is_private_account = 0 if is_private_account == "false" else 1

        #creating user object
        user_details = user.User(account_name, first_name, last_name, email, encrypt_password(password), phone_number, is_private_account,location)
        
        #validating the user object
        if(user_details.valid == False) :
            return {"status" : "failure", "message" : user_details.error}

        #sql command for creating new user
        sql_command = 'INSERT INTO user_profile(user_handle, first_name, last_name, \
                        email, salted_password,  private_account, location) \
                        VALUES ("%s", "%s", "%s", "%s", "%s", "%d", "%s" )' % \
                        (user_details.account_name, user_details.first_name, user_details.last_name, user_details.email, user_details.password, user_details.is_private_account, user_details.location)

        try :
            self.cursor.execute(sql_command)
            self.conn.commit()

            return {"status": "success", "code": "accepted","details": {"id": user_details.account_name}}
        except :
            self.conn.rollback()
            return "Failed to Sign up"


    #login route
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def login(self,**kwargs) :
        saved_args = locals()

        account_handle = saved_args['kwargs']['account_handle or email']
        password = saved_args['kwargs']['password']

        #sql command for login request
        sql_command = "SELECT * FROM user_profile WHERE user_handle = '%s'" % account_handle

        try :
            self.cursor.execute(sql_command)
            user_profile = self.cursor.fetchall()

            #fetching password from sql
            for row in user_profile :
                fetched_password = row[11]
            password = password.strip()

            #checking if the password is correct
            result = check_password(fetched_password, password)
            
            if(result):
                current_time = datetime.now().strftime("%H:%M:%S")

                token = get_jwt_token(account_handle)

                return {"status": "success", "code": "ACCEPTED", "details": {"login_time" : current_time, "location" : "India"},"access_token": token}
            else :
                return {"status": "failure", "message": "Password is incorrect"}
        except:
            return "User not found"


    #follow user route
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def follow_user(self,user_handle,token) :

        my_user_handle = get_user_handle_using_token(token)

        # validating the follow request
        is_valid = validate_follow_request(user_handle, my_user_handle)
        if(is_valid[0] == False) :
            return {"status" : "failed", "message" : is_valid[1]}

        # sql command for creating follow request
        sql_command = "INSERT INTO follows (user_handle,followed_by_user_handle,is_mutual) values('%s', '%s', '%d')" % (user_handle.strip(), my_user_handle,0)

        try :
            self.cursor.execute(sql_command)
            self.conn.commit()       
            return {"status": "success", "code": "SUCCESS", "details": {}}
        except :
            self.conn.rollback()
            return {"status" : "failed"}
    

    #post tweet route
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def post_tweet(self, tweet_id, created_time, tweet, location, is_reply, token) :

        my_user_handle = get_user_handle_using_token(token)
        is_reply = 0 if is_reply == "false" else 1

        # creating the new tweet object
        tweet_details = tweets.Tweet(tweet_id, created_time, tweet, location, my_user_handle, is_reply)
    
        # validating the tweet by object
        if(tweet_details.valid == False) :
            return {"status" : "failed", "message" : tweet_details.error}
        
        # validating the tweet if already exists
        is_valid = tweet_details.validate_tweet(tweet_id)

        if(is_valid[0] == False) :
            return {"status" : "failed", "message" : is_valid[1]}

        # sql command for creating tweet
        sql_command = "INSERT INTO tweets (tweet_id, created_time,\
             tweet, location, created_by, is_reply) VALUES \
                ('%s', '%s', '%s', '%s','%s','%d')" % \
                    (tweet_details.tweet_id, tweet_details.created_time, tweet_details.tweet \
                        ,tweet_details.location, tweet_details.created_by, tweet_details.is_reply)

        try :     
            self.cursor.execute(sql_command)
            self.conn.commit()
            return {"status": "success", "code": "accepted","details": {"tweet_id": tweet_details.tweet_id}}
        except :
            self.conn.rollback()
            return "Failed to post tweet"


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def tweet_activity(self, tweet_id, activity, token) :
        
        my_user_handle = get_user_handle_using_token(token)
        # getting sql command according to the activity type
        sql_command = get_sql_command_for_activity(activity, tweet_id, my_user_handle)
        
        #validating the tweet activity
        is_valid = validate_tweet_activities(tweet_id,activity,my_user_handle)

        if(is_valid[0] == False) :
            return {"status" : "failed", "message" : is_valid[1]}

        try :
            self.cursor.execute(sql_command)
            self.conn.commit()
            return {"status": "success", "code": "SUCCESS","details": {"tweet_id": tweet_id}}
        except :
            self.conn.rollback()
            return "Failed to post activity"


    #reply tweet route
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def reply_tweet(self, target_tweet_id, tweet_id, created_time, tweet, location, is_reply, token):
        
        my_user_handle = get_user_handle_using_token(token)
        is_reply = 1
        #creating a tweet object
        tweet_details = tweets.Tweet(tweet_id, created_time, tweet, location, my_user_handle, is_reply)

        if(tweet_details.valid == False) :
            return {"status" : "failed", "message" : tweet_details.error}
        
        #validating the tweet object
        is_valid = tweet_details.validate_tweet(tweet_id)

        if(is_valid[0] == False) :
            return {"status" : "failed", "message" : is_valid[1]}

        #sql command for creating tweet
        sql_command_for_tweet = "INSERT INTO tweets (tweet_id, created_time,\
            tweet, location, created_by, is_reply) VALUES \
            ('%s', '%s', '%s', '%s','%s','%d')" % \
            (tweet_details.tweet_id, tweet_details.created_time, tweet_details.tweet, tweet_details.location, tweet_details.created_by, tweet_details.is_reply)
        sql_command_for_audit = "INSERT INTO audit (tweet_id,replied_by, replied_to) VALUES ('%s', '%s', '%s')" % (tweet_details.tweet_id, my_user_handle, target_tweet_id)

        try :
            self.cursor.execute(sql_command_for_tweet)
            self.cursor.execute(sql_command_for_audit)
            self.conn.commit()
            return {"status": "success", "code": "SUCCESS","details": {"tweet_id": tweet_id}}
        except :
            self.conn.rollback()
            return "Failed to reply tweet"


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def tweet(self, activity, tweet_id, token) :

        my_user_handle = get_user_handle_using_token(token)

        if activity == "likes" :
            details = getLikesInfo(tweet_id)
            if(details != "error"):
                return {"status" : "success", "code" : "SUCCESS", "details" : details}
            else :
                return {"status" : "failed", "code" : "FAILED"}

        elif activity == "retweets" :
            details = getRetweetsInfo(tweet_id)

            if(details != "error"):
                return {"status" : "success", "code" : "SUCCESS", "details" : details}
            else :
                return {"status" : "failed", "code" : "FAILED"}

        elif activity == "replies" :

            details = getRepliesInfo(tweet_id)

            if(details != "error"):
                return {"status" : "success", "code" : "SUCCESS", "details" : details}
            else :
                return {"status" : "failed", "code" : "FAILED"}

            
    #home timeline route
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def home_timeline(self) :

        # my_user_handle = get_user_handle_using_token(token)
        # sql_command = "SELECT * FROM tweets where user_handle != '%s'" % my_user_handle
        sql_command = "SElECT * FROM tweets"

        try :
            conn = connection()
            cursor = conn.cursor()
            cursor.execute(sql_command)
            user_profile = cursor.fetchall()
            details = getTweets(user_profile)
            return {"status" : "success", "code" : "SUCCESS", "details" : details}
        except :
            return {"status" : "falied", "code" : "Cannot get timeline"}


    # user timeline route
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def user_timeline(self, order, action, token) :

        my_user_handle = get_user_handle_using_token(token)
        sql_command = get_sql_command_for_action(action, my_user_handle)

        try :
            self.cursor.execute(sql_command)
            tweet_ids = self.cursor.fetchall()
            tweet_id_list = []
            for row in tweet_ids :
                tweet_id_list.append(row[0])
            details = getTweetsById(tweet_id_list, order, action)
            return {"status" : "success", "code" : "SUCCESS", "details" : details}
        except :
            return "error"


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def search_users(self, user_name, token, pattern="", location="") :

        my_user_handle = get_user_handle_using_token(token)
        sql_command = get_sql_command_for_location(user_name, location)

        try :
            self.cursor.execute(sql_command)
            user_ids = self.cursor.fetchall()
            user_id_list = getAccountsList(user_ids)
            return {"status" : "success", "code" : "SUCCESS", "details" : user_id_list}
        except :
            return {"status" : "falied", "code" : "FAILURE", "details" : "No results found"}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def search_keyword(self, keyword, token) :

        my_user_handle = get_user_handle_using_token(token)
        sql_command = "SELECT * FROM tweets WHERE tweet REGEXP '%s'" % keyword

        try :
            self.cursor.execute(sql_command)
            tweets = self.cursor.fetchall()
            details = getTweets(tweets)
            return {"status" : "success", "code" : "SUCCESS", "details" : details}
        except :
            return {"status" : "falied", "code" : "FAILURE", "details" : "No results found"}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def search_hashtag(self, hashtag, token) :

        my_user_handle = get_user_handle_using_token(token)
        sql_command = "SELECT * FROM tweets WHERE tweet REGEXP '%s'" % ("#"+hashtag)

        try :
            self.cursor.execute(sql_command)
            tweets = self.cursor.fetchall()
            details = getTweets(tweets)
            return {"status" : "success", "code" : "SUCCESS", "details" : details}
        except :
            return {"status" : "falied", "code" : "FAILURE", "details" : "Hashtag not found"}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def view_trends(self, token, location="", search_by="") :

        my_user_handle = get_user_handle_using_token(token)

        #getting trends from function
        details = getTrends(location, search_by)

        return {"status" : "success", "code" : "SUCCESS", "details" : details}
        

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def message(self, user_handle, message, token) :
        
        my_user_handle = get_user_handle_using_token(token)

        #checking whether the both users are same
        if(user_handle == my_user_handle) :
            return {"status" : "failure", "code" : "FAILED", "details" : "You cannot send message to you"}
        
        if(message == ""):
            return {"status" : "failure", "code" : "FAILED", "details" : "Empty message"}

        sql_command = "INSERT INTO connection (from_user, to_user, message) VALUES ('%s', '%s', '%s')" % (my_user_handle, user_handle, message)

        try :
            self.cursor.execute(sql_command)
            self.conn.commit()
            return {"status" : "success", "code" : "SUCCESS", "details" : {}}
        except :
            return {"status" : "failed", "code" : "Message cannot be sent"}

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type, authorization"


#starts web server and calls the specified class
if __name__ == "__main__" :
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.CORS.on' : True,
        },
        '/static' : {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public',
        }
    }
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.quickstart(Twitter(),'/twitter',conf)
    cherrypy.quickstart(Twitter(),'/twitter/tweet',conf)