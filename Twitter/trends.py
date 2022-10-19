from db import connection
from activities import getLikesCount, getRetweetsCount, getRepliesCount, getUserName

def getTrends(location="", search_by="") :

    conn = connection()
    cursor = conn.cursor()
    if(location == "") :
        sql_command = "SELECT tweet, tweet_id FROM tweets"
    else :
        sql_command = "SELECT tweet, tweet_id FROM tweets where location='%s'" % location

    tweet_details = []
    try :
        cursor.execute(sql_command)
        results = cursor.fetchall()

        for row in results :
            tweet_details.append([row[0], row[1]])
    except :
        print( "error")

    if(tweet_details == []) :
        print("No trends found")
    
    if search_by == "" :
        search_by = "hashtag"
    
    # for get trending using hashtags
    search_list = []
    if search_by == "hashtag" :
        for tweet in tweet_details :
            for word in tweet[0].split() :
                if "#" in word :
                    search_list.append(word)
    
    else :
        for tweet in tweet_details :
            for word in tweet[0].split() :
                if len(word) > 5 and "#" not in word:
                    search_list.append(word)
    

    wordfreq = {}
    for raw_word in search_list:
        word = raw_word.strip()
        if word not in wordfreq:
            wordfreq[word] = 0 
        wordfreq[word] += 1
    sorted_hashtags = sorted(wordfreq, key = wordfreq.get)[::-1]

    trending_dict = {}
    trending_list = [[] for i in range(len(sorted_hashtags))]

    for ind in range(len(sorted_hashtags)):
        for tweet in tweet_details :
            if sorted_hashtags[ind] in tweet[0].split() :
                trending_list[ind].append(tweet[1])
    
    for ind_list in range(len(trending_list)):
        for ind_tweet in range(len(trending_list[ind_list])):
            trending_list[ind_list][ind_tweet] = getTweetById(trending_list[ind_list][ind_tweet])

    for ind in range(1,len(trending_list)+1) :
        trending_dict["trending"+str(ind)+" "+sorted_hashtags[ind-1]] = trending_list[ind-1]

    return trending_dict      
        
    
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
   
getTrends()
    

    