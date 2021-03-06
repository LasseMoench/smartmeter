import connexion
from flask import render_template, make_response
import sqlite3
import time
from datetime import datetime, time as dttime
import json

conn = sqlite3.connect('energy.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS energy(timestamp INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS connection_loss(timestamp INTEGER, duration INTEGER, ticks_missed INTEGER)')
conn.commit()


def tick():
    ts = time.time()
    print("13Wh consumed! Timestamp is: {}. Time readable: {}.".format(ts, datetime.utcfromtimestamp(ts).strftime(
        '%H:%M:%S %d-%m-%Y')))

    c.execute("INSERT INTO energy VALUES ({})".format(ts))
    conn.commit()


def render_html():
    c.execute("SELECT Count(*) FROM energy")
    total_power_in_db = c.fetchone()
    total_power = float('%.2f' % (total_power_in_db[0] * 13.33333 + 25503550))

    midnight = datetime.combine(datetime.today(), dttime.min)
    c.execute("SELECT Count(*) FROM energy WHERE timestamp > {}".format(midnight.timestamp()))
    ticks_today = c.fetchone()
    daily_power = float('%.2f' % (ticks_today[0] * 13.33333))

    # TODO: Implement average daily power here for each day

    c.execute("SELECT * FROM energy ORDER BY energy._ROWID_ DESC LIMIT 2")
    last_2_timestamps = c.fetchall()

    time_diff_secs = last_2_timestamps[0][0] - last_2_timestamps[1][0]

    # Time it took to consume 13.3Wh extrapolated to hourly energy use
    current_power = float('%.2f' % (13.33333 / time_diff_secs * 3600))

    c.execute("SELECT timestamp FROM energy WHERE timestamp > {}".format(midnight.timestamp()))
    rows = c.fetchall()

    data_points = []

    c.execute("SELECT * FROM energy WHERE timestamp > {}".format(midnight.timestamp()))

    data_rows = c.fetchall()

    for i in range(1, len(data_rows)):
        seconds = data_rows[i][0] - data_rows[i-1][0]
        watt = int(13.33333 / seconds * 3600)
        timestamp_avg = (data_rows[i][0] + data_rows[i-1][0]) / 2
        data_points.append([timestamp_avg, watt])

    # print(data_points)
    
    headers = {'Content-Type': 'text/html'}

    return make_response(render_template('index.html', current_power=current_power, total_power=total_power,
                                         daily_power=daily_power, data_points=json.dumps(data_points)), 200,
                         headers)


def get_lcd_info():
    midnight = datetime.combine(datetime.today(), dttime.min)
    c.execute("SELECT Count(*) FROM energy WHERE timestamp > {}".format(midnight.timestamp()))
    ticks_today = c.fetchone()
    daily_power = float('%.2f' % (ticks_today[0] * 13.33333))

    c.execute("SELECT * FROM energy ORDER BY energy._ROWID_ DESC LIMIT 2")
    last_2_timestamps = c.fetchall()

    time_diff_secs = last_2_timestamps[0][0] - last_2_timestamps[1][0]

    # Time it took to consume 13.3Wh extrapolated to hourly energy use
    current_power = int(13.33333 / time_diff_secs * 3600)

    result = {"daily_power": daily_power, "current_power": current_power}

    return result


def count_connection_loss(duration, ticks_missed):
    ts = time.time()
    print("ESP has regained connection! Time: {}".format(datetime.utcfromtimestamp(ts).strftime(
        '%H:%M:%S %d-%m-%Y')))

    duration_in_s = int(float(duration) / 1000)

    c.execute("INSERT INTO connection_loss VALUES ({}, {}, {})".format(ts, duration_in_s, ticks_missed))
    conn.commit()


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
