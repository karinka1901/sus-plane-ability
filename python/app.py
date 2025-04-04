import json
from dotenv import load_dotenv
import config
import os

from flask import Flask, request
from flask_cors import CORS

from game import Game
import psycopg2

load_dotenv()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
print("Connecting to DB with user:", os.environ.get('DB_USER'))
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASS'] = '123'


config.conn = psycopg2.connect(
    host=os.environ.get('HOST'),
    port=os.environ.get('PORT'),
    database=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASS')
)
config.conn.autocommit = True
cursor = config.conn.cursor()



def fly(id, dest, consumption=0, player=None):
    if id==0:
        game = Game(0, dest, consumption, player)
    else:
        game = Game(id, dest, consumption)
    game.location[0].fetchWeather(game)
    game.location[0].fetchData(game)
    nearby = game.location[0].find_nearby_airports()
    for a in nearby:
        game.location.append(a)
    json_data = json.dumps(game, default=lambda o: o.__dict__, indent=4)
    return json_data


@app.route('/flyto')
def flyto():
    args = request.args
    id = args.get("game")
    dest = args.get("dest")
    consumption = args.get("consumption")
    json_data = fly(id, dest, consumption)
    print("*** Called flyto endpoint ***")
    return json_data


@app.route('/newgame')
def newgame():
    args = request.args
    player = args.get("player")
    dest = args.get("loc")
    json_data = fly(0, dest, 0, player)
    return json_data

if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)
