
import psycopg2
from pgConfig import pgConfig

def pgConnect():
    """ Connect to the PostgreSQL database server and return curser (cur) """
    conn = None
    returnValue = False

    try:
        # read connection parameters
        action = "pgConnect - Get configuration calling pgConfig(): "
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgConnect - Connect to PostGres database: "
        conn = psycopg2.connect(**params)
     
        # create a cursor
        cur = conn.cursor()
    
        # Verify connection to PostgresSQL
        action = "pgConnect - SELECT version(): "
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()

        if __name__ == '__main__':
            print('Connected to PosgreSQL successfully.')
            print(f'PostgreSQL database version:  {db_version} ')

        # Verify presens of tables.´
        cur.execute("SELECT FROM pg_tables \
                    WHERE schemaname = 'public' \
                    AND tablename  = 'meter_metadata' \
                    OR tablename  = 'meter_status' \
                    OR tablename  = 'meter_totals' \
                    OR tablename  = 'consumption'") 
        
        if len(cur.fetchall()) == 4:  
            returnValue = True
        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)
        returnValue = None

    finally:
        if conn is not None:
            conn.close()
            if __name__ == '__main__':
                print('Database connection closed.')
    
    return returnValue


if __name__ == '__main__':
    if pgConnect():
        print("Connect to Postgres DB successful.")
    else:
        print("Connect to Postgres DB successful, BUT not tables found!!!")
    