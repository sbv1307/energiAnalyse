import psycopg2

from pgConfig import pgConfig

def pgGetNumberOfRows(table_name):

    # Query Meter metadata from table meter_metadata
    conn = None
    number_of_rows = None

    try:
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgGetNumberOfRows - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Select pulse per kWh from table meter
        action = "pgGetNumberOfRows - SELECT count(*) FROM " + table_name

        cur.execute("SELECT count(*) \
                    FROM {}".format(table_name))

        number_of_rows = cur.fetchone()[0]

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

    return number_of_rows


if __name__ == '__main__':
    table_name = 'meter_status'
    number_of_rows = pgGetNumberOfRows(table_name)
    print(f'Number of rows in table name \'{table_name}\': {type(number_of_rows)} {number_of_rows}')
