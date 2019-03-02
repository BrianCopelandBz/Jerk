from flask import Flask, render_template, jsonify, request
from threading import Lock
from werkzeug.serving import run_simple

import sqlite3

app = Flask(__name__)

thread = None
thread_lock = Lock()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def average_temp(temp_score):
    if temp_score <= 1.3:
        return "mostly not a jerk"
    elif temp_score > 1.3 and temp_score <= 1.7:
        return "between not a jerk and a tiny bit of a jerk"
    elif temp_score > 1.7 and temp_score <= 2.3:
        return "mostly just a tiny bit of a jerk"
    elif temp_score > 2.3 and temp_score <= 2.7:
        return "between a tiny bit and a fair amount of a jerk"
    elif temp_score > 2.7 and temp_score <= 3.3:
        return "mostly a fair amount of jerk"
    elif temp_score > 3.3 and temp_score <= 3.7:
        return "between a fair amount and pretty jerky"
    elif temp_score > 3.7 and temp_score <= 4.3:
        return "pretty jerky"
    elif temp_score > 4.3 and temp_score <= 4.7:
        return "between pretty jerky and a total jerk"
    elif temp_score > 4.7:
        return "mostly a total jerk"
    else:
        return "broken"

@app.route('/')
def home():
    with sqlite3.connect('jerk.db') as conn:
        cget = conn.cursor()
        cget.row_factory = dict_factory
        cget.execute("""SELECT jerktemp, datetime(sqltime, 'localtime', '-1 hour') as updatedt FROM jerk ORDER BY sqltime DESC LIMIT 50""")
        x = cget.fetchall()
        current_update_dt = datetime.strptime(x[0]['updatedt'], '%Y-%m-%d %H:%M:%S').strftime('%A %b %d %I:%M %p')
        cget.execute("""SELECT SUM(CASE WHEN jerktemp = 'too-cold' then 1 WHEN jerktemp = 'cold' then 2 WHEN jerktemp = 'perfect' then 3
        WHEN jerktemp = 'lukewarm' then 4 WHEN jerktemp = 'hot' then 5 ELSE 0 END) as score, COUNT(*) as theCount FROM jerk;""")
        agg = cget.fetchone()
        total_updates = agg['theCount']
        total_temp_string =  average_temp(agg['score'] / agg['theCount'])
        cget.execute("""SELECT SUM(CASE WHEN jerktemp = 'too-cold' then 1 WHEN jerktemp = 'cold' then 2 WHEN jerktemp = 'perfect' then 3
        WHEN jerktemp = 'lukewarm' then 4 WHEN jerktemp = 'hot' then 5 ELSE 0 END) as score, COUNT(*) as theCount FROM jerk
        WHERE sqltime > datetime(CURRENT_TIMESTAMP, '-1 day');""")
        today_agg = cget.fetchone()
        today_updates = today_agg['theCount']
        today_temp_string =  average_temp(today_agg['score'] / today_agg['theCount'])
    return render_template('home.html',
        temp=x[0]['jerktemp'],
        update=current_update_dt,
        history=x,
        total_updates=total_updates,
        total_temp_string=total_temp_string,
        today_updates=today_updates,
        today_temp_string=today_temp_string
        )

@app.route('/test')
def test_site():
    return render_template('test.html')

@app.route('/test2')
def test2_site():
    return render_template('test2.html')

@app.route('/test3')
def test3_site():
    return render_template('test3.html')

@app.route('/[secret_jerk_url]')
def test_switch():
    return render_template('index.html')

@app.route('/_new_too_cold')
def new_too_cold():
    with sqlite3.connect('jerktemp.db') as conn:
        cput = conn.cursor()
        cput.execute("INSERT INTO jerk (sqltime, jerktemp) VALUES (CURRENT_TIMESTAMP, ?)", ("too-cold",))

    return jsonify(result="updated to too cold")

@app.route('/_new_cold')
def new_cold():
    with sqlite3.connect('jerktemp.db') as conn:
        cput = conn.cursor()
        cput.execute("INSERT INTO jerk (sqltime, jerktemp) VALUES (CURRENT_TIMESTAMP, ?)", ("cold",))

    return jsonify(result="updated to cold")


@app.route('/_new_perfect')
def new_perfect():
    with sqlite3.connect('jerktemp.db') as conn:
        cput = conn.cursor()
        cput.execute("INSERT INTO jerk (sqltime, jerktemp) VALUES (CURRENT_TIMESTAMP, ?)", ("perfect",))
    return jsonify(result="updated to perfect")


@app.route('/_new_lukewarm')
def new_lukewarm():
    with sqlite3.connect('jerktemp.db') as conn:
        cput = conn.cursor()
        cput.execute("INSERT INTO jerk (sqltime, jerktemp) VALUES (CURRENT_TIMESTAMP, ?)", ("lukewarm",))

    return jsonify(result="updated to lukewarm")

@app.route('/_new_hot')
def new_hot():
    with sqlite3.connect('jerktemp.db') as conn:
        cput = conn.cursor()
        cput.execute("INSERT INTO jerk (sqltime, jerktemp) VALUES (CURRENT_TIMESTAMP, ?)", ("hot",))

    return jsonify(result="updated to hot")

application = app

if __name__ == '__main__':
    app.run(threaded=True)
