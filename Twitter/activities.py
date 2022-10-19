
from db import connection
import jwt

def getTweets(user_profile):
    
    details = []
    for row in user_profile:
        tweet_dict = {}
        tweet_dict["tweet_id"] = row[0]
        tweet_dict["tweet"] = row[2]
        tweet_dict["tweeted_by"] = getUserName(row[4])
        tweet_dict["tweeter_id"] = row[4]
        tweet_dict["likes_count"] = getLikesCount(row[0])
        tweet_dict["retweets_count"] = getRetweetsCount(row[0])
        tweet_dict["replies_count"] = getRepliesCount(row[0])
        details.append(tweet_dict)
    
    return details

def getTweetsById(tweets_id, order, action) :

    conn = connection()
    cursor = conn.cursor()

    details = []
    for id in tweets_id:
        sql_command = "SELECT * FROM tweets WHERE tweet_id='%s'" % id
        cursor.execute(sql_command)
        tweet = cursor.fetchone()

        tweet_dict = {}
        tweet_dict["tweet_id"] = tweet[0]
        tweet_dict["tweet"] = tweet[2]
        tweet_dict["tweeted_by"] = getUserName(tweet[4])
        tweet_dict["tweeter_id"] = tweet[4]
        tweet_dict["likes_count"] = getLikesCount(tweet[0])
        tweet_dict["retweets_count"] = getRetweetsCount(tweet[0])
        tweet_dict["replies_count"] = getRepliesCount(tweet[0])
        details.append(tweet_dict)

    if(action == "likes") :
        details.sort(key = lambda x:x['likes_count'])

        if(order == "decreasing") :
            details = details[::-1]
    else :
        details.sort(key = lambda x:x['retweets_count'])

        if(order == "decreasing") :
            details = details[::-1]
        
    conn.close()
    return details

def getLikesCount(tweet_id):

    conn = connection()
    cursor = conn.cursor()

    sql_command = "select count(liked_by) from audit where tweet_id='%s'" % tweet_id

    try :
        cursor.execute(sql_command)
        
        likes_count = cursor.fetchone()[0]
        return likes_count
    except :
        print("error")

    conn.close()

def getRetweetsCount(tweet_id):

    conn = connection()
    cursor = conn.cursor()

    sql_command = "select count(retweeted_by) from audit where tweet_id='%s'" % tweet_id

    try :
        cursor.execute(sql_command)
        retweets_count = cursor.fetchone()[0]
        return retweets_count
    except :
        print("error")

def getRepliesCount(tweet_id):

    conn = connection()
    cursor = conn.cursor()

    sql_command = "select count(replied_by) from audit where tweet_id='%s'" % tweet_id

    try :
        cursor.execute(sql_command)
        replies_count = cursor.fetchone()[0]
        return replies_count
    except :
        print("error")

def getUserName(userId) :
    
    conn = connection()
    cursor = conn.cursor()

    sql_command = "select first_name, last_name from user_profile where user_handle='%s'" % userId

    try :
        cursor.execute(sql_command)
        user_name = cursor.fetchone()
        user_name = user_name[0] +" "+user_name[1]
        conn.close()
        return user_name
        
    except :
        conn.close()
        print("error")

def getAccountsList(user_ids) :

    user_list = []
    for row in user_ids :
        user_dict = {}
        user_dict["account_handle"] = row[0]
        user_dict["account_name"] = row[1]+" "+row[2]
        user_list.append(user_dict)

    return user_list

def get_sql_command_for_activity(activity, tweet_id, my_user_handle) :
    if(activity == "like") :
        sql_command = "INSERT INTO audit (tweet_id,liked_by) VALUES ('%s', '%s')" % (tweet_id, my_user_handle)
    elif(activity == "retweet") :
        sql_command = "INSERT INTO audit (tweet_id,retweeted_by) VALUES ('%s', '%s')" % (tweet_id, my_user_handle)
    elif(activity == "bookmark") :
        sql_command = "INSERT INTO audit (tweet_id,bookmarked_by) VALUES ('%s', '%s')" % (tweet_id, my_user_handle)
    return sql_command

def get_user_handle_using_token(token) :
    decoded_payload = jwt.decode(token, "selvaganapathy", algorithms=["HS256"])
    my_user_handle = decoded_payload["name"].strip()
    return my_user_handle
    
def get_sql_command_for_location(user_name, location) :
    if(location != "") :
        sql_command = "SELECT * FROM user_profile WHERE first_name REGEXP '%s' OR last_name REGEXP '%s' AND location LIKE '%s'" % (user_name, user_name, location)
    else :
        sql_command = "SELECT * from user_profile where first_name REGEXP '%s' OR last_name REGEXP '%s'" % (user_name, user_name)
    return sql_command

def get_sql_command_for_action(action, my_user_handle) :
    if(action == "likes") :
        sql_command = "SELECT DISTINCT tweet_id from audit WHERE liked_by = '%s'" % my_user_handle
    elif(action == "retweets") :
        sql_command = "SELECT DISTINCT tweet_id from audit WHERE retweeted_by = '%s'" % my_user_handle
    return sql_command

def validate_follow_request(user_handle, my_user_handle) :
    valid = True
    error = []
    if(user_handle == my_user_handle) :
        valid = False
        error.append("You cannot follow you")
        return [valid,error]

    else :
        conn = connection()
        cursor = conn.cursor()

        sql_command = "SELECT * FROM user_profile WHERE user_handle='%s'" % (user_handle)

        try :
            cursor.execute(sql_command)
            user_name = cursor.fetchone()[0]
        except :
            valid = False
            error.append("User not found")
            return [valid, error]

        sql_command = "SELECT user_handle FROM follows where followed_by_user_handle='%s'" % (my_user_handle)
        
        try :
            cursor.execute(sql_command)
            user_name = cursor.fetchall()
            users_list = []
            for rows in user_name :
                users_list.append(rows[0])
            if user_handle in users_list :
                valid = False
                error.append("You are already following this user")
                return [valid, error]

        except :
            valid = True
        return [valid,error]

def validate_tweet_activities(tweet_id, activity, my_user_handle) :

    conn = connection()
    cursor = conn.cursor()
    valid = True
    error = []
    #validating the like activity
    if(activity == "like") :
        
        sql_command = "SELECT tweet_id from audit where liked_by = '%s'" % my_user_handle

        try :
            cursor.execute(sql_command)
            results = cursor.fetchall()
            tweet_id_list = []
            for row in results :
                tweet_id_list.append(row[0])

            if tweet_id in tweet_id_list :
                valid = False
                error.append("You have already liked this tweet")
                return [valid,error]
        except :
            return [valid,error]

    #validating the retweet activity
    if(activity == "retweet") :

        sql_command = "SELECT tweet_id from audit where retweeted_by = '%s'" % my_user_handle

        try :
            cursor.execute(sql_command)
            results = cursor.fetchall()
            tweet_id_list = []
            for row in results :
                tweet_id_list.append(row[0])

            if tweet_id in tweet_id_list :
                valid = False
                error.append("You have already retweeted this tweet")
                return [valid,error]
        except :
            return [valid,error]

    #validating the bookmark activity
    if(activity == "bookmark") :

        sql_command = "SELECT tweet_id from audit where bookmarked_by = '%s'" % my_user_handle

        try :
            cursor.execute(sql_command)
            results = cursor.fetchall()
            tweet_id_list = []
            for row in results :
                tweet_id_list.append(row[0])

            if tweet_id in tweet_id_list :
                valid = False
                error.append("You have already bookmarked this tweet")
                return [valid,error]
        except :
            return [valid,error]
    return [valid,error]

def getLikesInfo(tweet_id) :
    conn = connection()
    cursor = conn.cursor()

    sql_command = "SELECT liked_by from audit where tweet_id = '%s' and liked_by IS NOT NULL" % tweet_id
    
    user_id_list = []
    try :
        cursor.execute(sql_command)
        results = cursor.fetchall()

        
        for row in results :
            user_id_list.append(row[0])
    except :
        return "error"
    
    if(user_id_list == []) :
        return "No likes info found"
    user_name_list = []
    for user_id in user_id_list :
        sql_command = "SELECT first_name, last_name FROM user_profile where user_handle = '%s'" % user_id

        try :
            cursor.execute(sql_command)
            results = cursor.fetchone()
            user_name_list.append(results[0] + results[1])
        except :
            return "error"

    details = []
    for ind in range(len(user_id_list)) :
        likes_dict = {}
        likes_dict["liked_by_handle"] = user_id_list[ind]
        likes_dict["liked_by_name"] = user_name_list[ind]
        
        details.append(likes_dict)
    
    return details

def getRetweetsInfo(tweet_id) :
    conn = connection()
    cursor = conn.cursor()

    sql_command = "SELECT retweeted_by from audit where tweet_id = '%s' and retweeted_by IS NOT NULL" % tweet_id
    
    user_id_list = []
    try :
        cursor.execute(sql_command)
        results = cursor.fetchall()

        
        for row in results :
            user_id_list.append(row[0])
    except :
        return "error"
    
    if(user_id_list == []) :
        return "No retweets info found"
    user_name_list = []
    for user_id in user_id_list :
        sql_command = "SELECT first_name, last_name FROM user_profile where user_handle = '%s'" % user_id

        try :
            cursor.execute(sql_command)
            results = cursor.fetchone()
            user_name_list.append(results[0] + results[1])
        except :
            return "error"

    details = []
    for ind in range(len(user_id_list)) :
        retweets_dict = {}
        retweets_dict["retweeted_by_handle"] = user_id_list[ind]
        retweets_dict["retweeted_by_name"] = user_name_list[ind]
        
        details.append(retweets_dict)
    
    return details

def getRepliesInfo(tweet_id) :
    
    conn = connection()
    cursor = conn.cursor()

    sql_command = "SELECT tweet_id FROM audit where replied_to = '%s'" % tweet_id

    tweet_id_list = []

    try :
        cursor.execute(sql_command)
        results = cursor.fetchall()
        for row in results :
            tweet_id_list.append(row[0])
    except :
        return "error"
    
    if(tweet_id_list == []) :
        return "No replies found"

    details = []
    
    for tweet_id in tweet_id_list :
        tweet_dict = getTweetById(tweet_id)
        details.append(tweet_dict)

    return details

def getTweetById(tweet_id):
    conn = connection()
    cursor = conn.cursor()
    sql_command = "SELECT * FROM tweets WHERE tweet_id='%s'" % tweet_id
    try :
        cursor.execute(sql_command)
        results = cursor.fetchall()
        
        tweet_dict = {}
        for row in results:
            tweet_dict["tweet_id"] = row[0]
            tweet_dict["tweet"] = row[2]
            tweet_dict["tweeted_by"] = getUserName(row[4])
            tweet_dict["tweeter_id"] = row[4]
            tweet_dict["likes_count"] = getLikesCount(row[0])
            tweet_dict["retweets_count"] = getRetweetsCount(row[0])
            tweet_dict["replies_count"] = getRepliesCount(row[0])

        return tweet_dict
    except :
        return "error"