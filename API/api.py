import connexion
import sqlite3
import time
from datetime import datetime, time as dttime

conn = sqlite3.connect('energy.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS energy(timestamp INTEGER)')


def tick():
    ts = time.time()
    print("13Wh consumed! Timestamp is: {}. Time readable: {}.".format(ts, datetime.utcfromtimestamp(ts).strftime(
            '%H:%M:%S %d-%m-%Y')))

    c.execute("INSERT INTO energy VALUES ({})".format(ts))
    conn.commit()


def get_frontend_info():

    c.execute("SELECT Count(*) FROM energy")
    total_power_in_db = c.fetchone()
    total_power = int(total_power_in_db) * 13.33333 + 25477.1

    midnight = datetime.combine(datetime.today(), dttime.min)
    c.execute("SELECT Count(*) FROM energy WHERE timestamp > {}".format(midnight.timestamp()))
    ticks_today = c.fetchone()
    daily_power = int(ticks_today) * 13.33333

    # TODO: Implement average daily power here for each day

    # TODO: Implement current power draw (select last two ticks and calc power from that)

    return daily_power, total_power


app = connexion.App(__name__)
app.add_api('api.yaml')

# Set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app


def main():
    # Run our standalone gevent server
    app.debug = True
    app.run(port=8080, server='gevent')


if __name__ == '__main__':
    main()
