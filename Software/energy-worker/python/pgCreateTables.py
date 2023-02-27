import psycopg2
from pgConnect import pgConfig


def pgCreateTables():
# 'power_factor' en værdi, der kan korrigere det udrenede forbrug i watt
# 'diviation' For at reducere altallet af opsamlede data, bruges 'diviation' til at springe registrereingen af et timestamp og watt forbrug over
# hvis forbruget ligger inden for 'diviation' af foregående registrering. Kun første og sidste registrering af et givent forbrug i watt, er interessant at gemme
# 'interpolate_consupmtion' I situation hvor forbruget falder f.eks. til 0 watt, vil der aldrig kome flere pulser / timestamps for  det givne meter
# ved interpolatation kan der tilføjes et forbrug i data rækken, således at talrækken kan afsluttes og evt korrigeres, når der endelig kommer et timestamp
    """ create tables in the PostgreSQL database """
    create_commands = (
        """
        CREATE TABLE meter_metadata (
            meter_no SMALLSERIAL PRIMARY KEY,
            meter_name VARCHAR(255) NOT NULL,
            pulse_per_kWh SMALLINT NOT NULL,
            max_energy SMALLINT NOT NULL,
            power_factor DECIMAL NOT NULL,
            deviation_pct SMALLINT NOT NULL
        )
        """,
        """ CREATE TABLE meter_status (
            upper_index BIGINT NOT NULL,
            meter_no SMALLINT NOT NULL,
            reference_watt_consumption SMALLINT NOT NULL,
            meter_counts INTEGER NOT NULL,
            kWh DECIMAL NOT NULL,
            pulse_time_stamp BIGINT NOT NULL,
            pulse_period BIGINT NOT NULL,
            cor_time_stamp TIMESTAMP NOT NULL,
            time_stamp TIMESTAMP NOT NULL,
            PRIMARY KEY (meter_no),
            FOREIGN KEY (meter_no)
                REFERENCES meter_metadata (meter_no)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """ CREATE TABLE consumption (
            index BIGSERIAL,
            meter_no SMALLINT NOT NULL,
            watt_consumption SMALLINT NOT NULL,
            meter_counts INTEGER NOT NULL,
            kWh DECIMAL NOT NULL,
            pulse_time_stamp BIGINT NOT NULL,
            pulse_period BIGINT NOT NULL,
            cor_time_stamp TIMESTAMP NOT NULL,
            time_stamp TIMESTAMP NOT NULL,
            PRIMARY KEY (index),
            FOREIGN KEY (meter_no)
                REFERENCES meter_metadata (meter_no)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)
    
    drop_commands = (
        """ DROP TABLE IF EXISTS consumption""", """ DROP TABLE IF EXISTS meter_status""","""DROP TABLE IF EXISTS meter_metadata"""
    )
    
    conn = None
    return_value = False
    try:
        action = "pgCreateTables - Get parms from pgConfig"
        # read the connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "Connect to database: "

        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        if __name__ == '__main__':
            # Drop tables
            print('Droppning tables')
            action = "Drop tables if they exists: "

            for command in drop_commands:
                cur.execute(command)

        # create table one by one
        action = "create table: "

        for command in create_commands:
           cur.execute(command)

        # Set tiezone for database
        action = "SET timezone: "

        cur.execute("SET timezone = 'CET'")

        # Get durrent time from postgres server
        action = "Get current time: "

        cur.execute("SELECT NOW()")
        time_stamp = cur.fetchone()[0]
        
        # Inserting values into the table meter
        action = "INSERT INTO meter: "

        insert_stmt = "INSERT INTO meter_metadata (meter_no,\
        meter_name, pulse_per_kWh, max_energy, power_factor, deviation_pct) VALUES (%s, %s, %s, %s, %s, %s)"
        data = [(1, 'Varmepumpe SMO 40', 100, 11000, 1.0, 10),
                (2, 'Kraftstik Værksted Garage', 100, 11000, 1.0, 10),
                (3, 'Kontor EDB', 1000, 2500, 1.0, 10),
                (4, 'Bryggers Teknik', 1000, 2500, 1.0, 10),
                (5, 'Garage', 1000, 2500, 1.0, 10),
                (6, 'Værksted Lager Loft', 1000, 2500, 1.0, 10),
                (7, 'Kontor 1. sal', 1000, 2500, 1.0, 10),
                ]   
        cur.executemany(insert_stmt, data)


        # Inserting values into the table meter_status
        action = "INSERT INTO meter_status: "

        upper_index = 0
        meter_no = 1
        reference_watt_consumption = int(0)
        meter_counts = int(0)
        kWh = float(0.0)
        pulse_time_stamp = int(0)
        pulse_period = int(-1)
        cor_time_stamp = time_stamp

        data = list()
        insert_stmt = "INSERT INTO meter_status (upper_index, meter_no,\
                    reference_watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        while meter_no < 8:
            data += [(upper_index, meter_no, reference_watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)]
            meter_no += 1
        cur.executemany(insert_stmt, data)

        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()

        return_value = True
    

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)
    finally:
        if conn is not None:
            conn.close()

    return return_value 

if __name__ == '__main__':
    pgCreateTables()
    print('Tables creatged successfully.')