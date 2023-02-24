import psycopg2

from pgConfig import pgConfig

def pgGetTimeStamp():
    # Query time stamp 
    conn = None

    try:
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "Connect to database: "

        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Set tiezone for database
        action = "SET timezone: "

        cur.execute("SET timezone = 'CET'")

        # get time for timeStamp
        action = "Get current time: "
        cur.execute("SELECT NOW()")
        timeStamp = cur.fetchone()[0]

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()
            
    return timeStamp

if __name__ == '__main__':
    print(f'Current Postgress Time Stamp: {pgGetTimeStamp()} ')

    







    