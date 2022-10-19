from db import connection


class Tweet :
    def __init__(self, tweet_id, created_time, tweet, location, created_by, is_reply) :
        
        self.error = []
        self.valid = True

        #validating tweet id
        if tweet_id == "" :
            self.valid = False
            self.error.append("Tweet id is empty")
        else :
            self.tweet_id = tweet_id

        #validating created_time
        if created_time == "" :
            self.valid = False
            self.error.append("Created time is empty")
        else :
            self.created_time = created_time

        #validating tweet
        if tweet == "" :
            self.valid = False
            self.error.append("Tweet is empty")
        else :
            self.tweet = tweet

        #validating location
        if location == "" :
            self.valid = False
            self.error.append("Location is empty")
        else :
            self.location = location

        #validating created_by
        if created_by == "" :
            self.valid = False
            self.error.append("Created by is empty")
        else :
            self.created_by = created_by
        
        #validating is_reply
        if is_reply == "" :
            self.valid = False
            self.error.append("is_reply is empty")
        else :
            self.is_reply = is_reply
    def validate_tweet(self, tweet_id) :
        conn = connection()
        cursor = conn.cursor()
        valid = True
        error = []

        sql_command = "SELECT tweet_id FROM tweets"

        try :
            cursor.execute(sql_command)
            results = cursor.fetchall()

            tweet_id_list = []
            for row in results :
                tweet_id_list.append(row[0])
            
            if tweet_id in tweet_id_list :
                valid = False
                error.append("Tweet already found with this id");
                
                conn.close()
                return [valid,error]
            
        except :
            conn.close()
            return [valid,error]
        return [valid,error]

    

