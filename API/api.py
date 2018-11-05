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
    total_power = int(total_power_in_db[0]) * 13.33333 + 25477100

    midnight = datetime.combine(datetime.today(), dttime.min)
    c.execute("SELECT Count(*) FROM energy WHERE timestamp > {}".format(midnight.timestamp()))
    ticks_today = c.fetchone()
    daily_power = int(ticks_today[0]) * 13.33333

    # TODO: Implement average daily power here for each day

    c.execute("SELECT * FROM energy ORDER BY energy._ROWID_ DESC LIMIT 2")
    last_2_timestamps = c.fetchall()

    time_diff_secs = last_2_timestamps[0][0] - last_2_timestamps[1][0]

    # Time it took to consume 13.3Wh extrapolated to hourly energy use
    current_power = 13.33333 / time_diff_secs * 3600

    frontend_info = {
        "current_power": float('%.2f' % current_power),
        "daily_power": float('%.2f' % daily_power),
        "total_power": float('%.2f' % total_power)
    }

    return frontend_info, 200, {'Access-Control-Allow-Origin': '*'}


app = connexion.App(__name__)
app.add_api('api.yaml')

# Set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app


def main():
    # Run our standalone gevent server
    app.debug = False
    app.run(port=8080, server='gevent', host='0.0.0.0')


if __name__ == '__main__':
    main()
