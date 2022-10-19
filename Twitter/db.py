import pymysql

# database connection using pymysql
def connection() :
    s = 'localhost'
    prt = 3306
    d = 'TwitterDB'
    u = 'root'
    p = 'selva2002'
    conn = pymysql.connect(host=s,port=prt,user=u,password=p,database=d)
    return conn

def setup_db() :
    conn = connection()
    cursor = conn.cursor()

    #creating the user_profile table

    sql_command_table1 = """CREATE TABLE IF NOT EXISTS user_profile 
    (user_handle VARCHAR(50) NOT NULL UNIQUE PRIMARY KEY,
     first_name VARCHAR(20),
     last_name VARCHAR(20),
     email VARCHAR(50),
     private_account BOOLEAN,
     salted_password VARCHAR(250),
     location VARCHAR(200),
     2fa_enabled BOOLEAN,
     is_verified BOOLEAN,
     is_deletion_scheduled BOOLEAN,
     profile_image VARCHAR(200),
     banner_image VARCHAR(200)) """

    cursor.execute(sql_command_table1)
    
    #creating the followers table
    sql_command_table2 = """
    CREATE TABLE IF NOT EXISTS follows
    (auto_number INTEGER AUTO_INCREMENT PRIMARY KEY,
    user_handle VARCHAR(50) NOT NULL,
    followed_by_user_handle VARCHAR(50) NOT NULL,
    is_mutual BOOLEAN,
    FOREIGN KEY(user_handle) REFERENCES user_profile(user_handle),
    FOREIGN KEY(followed_by_user_handle) REFERENCES user_profile(user_handle))
    """

    cursor.execute(sql_command_table2)

    #creating the tweets table
    sql_command_table3 = """
    CREATE TABLE IF NOT EXISTS tweets
    (tweet_id VARCHAR(50) NOT NULL PRIMARY KEY UNIQUE,
    created_time VARCHAR(50) NOT NULL,
    tweet VARCHAR(260) NOT NULL,
    location VARCHAR(50) NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    is_reply BOOLEAN NOT NULL,
    FOREIGN KEY (created_by) REFERENCES user_profile(user_handle))
    """

    cursor.execute(sql_command_table3)

    #creating the audit table
    sql_command_table4 = """
    CREATE TABLE IF NOT EXISTS audit
    (auto_number INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    tweet_id VARCHAR(50) NOT NULL,
    retweeted_by VARCHAR(50),
    liked_by VARCHAR(50),
    bookmarked_by VARCHAR(50),
    replied_by VARCHAR(50),
    replied_to VARCHAR(50),
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id),
    FOREIGN KEY (retweeted_by) REFERENCES user_profile(user_handle),
    FOREIGN KEY (liked_by) REFERENCES user_profile(user_handle),
    FOREIGN KEY (bookmarked_by) REFERENCES user_profile(user_handle),
    FOREIGN KEY (replied_by) REFERENCES user_profile(user_handle),
    FOREIGN KEY (replied_to) REFERENCES tweets(tweet_id))
    """

    cursor.execute(sql_command_table4)

    #creating the connection table
    sql_command_table5 = """
    CREATE TABLE IF NOT EXISTS connection
    (auto_number INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    from_user VARCHAR(50) NOT NULL,
    to_user VARCHAR(50) NOT NULL,
    tweet_id VARCHAR(50),
    message VARCHAR(255),
    is_mention BOOLEAN,
    is_message BOOLEAN,
    is_message_seen BOOLEAN,
    is_mention_seen BOOLEAN,
    FOREIGN KEY (from_user) REFERENCES user_profile(user_handle),
    FOREIGN KEY (to_user) REFERENCES user_profile(user_handle),
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id))
    """

    cursor.execute(sql_command_table5)

    conn.commit()
    conn.close()

setup_db()