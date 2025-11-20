from flask import Flask, render_template, request, jsonify
import mysql.connector
import datetime

app = Flask(__name__)

# Connect MySQL
db = mysql.connector.connect(
    host="yourhost",
    user="youruser",
    password="yourpassword",
    database="powermonitor"
)
cur = db.cursor()

@app.route('/api/update-dht-data', methods=['POST'])
def update_dht_data():
    data = request.json

    Voltage = data.get("Voltage")
    Current = data.get("Current")

    if Voltage is None or Current is None:
        return jsonify({"error": "Missing fields"}), 400

    # Calculate Power
    Power = float(Voltage) * float(Current)

    now = datetime.datetime.now()
    date = now.date()
    day = now.strftime("%A")
    time = now.strftime("%H:%M:%S")

    cur.execute("""
        INSERT INTO data (date, day, time, Voltage_V, Current_I, Power_W)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (date, day, time, Voltage, Current, Power))

    db.commit()

    return jsonify({"message": "Data stored"})


@app.route('/')
def index():
    return render_template('Frontend.html')


@app.route('/api/get-graph-data')
def get_graph_data():

    cur.execute("SELECT time, Voltage_V, Current_I FROM data ORDER BY ID DESC LIMIT 50")
    rows = cur.fetchall()

    labels = [row[0].strftime("%H:%M:%S") for row in rows]
    voltage = [row[1] for row in rows]
    current = [row[2] for row in rows]

    return jsonify({
        "labels": labels[::-1],
        "Voltage": voltage[::-1],
        "Current": current[::-1],
    })


# from flask import Flask, render_template, request, jsonify


# app = Flask(__name__)

# data_history = {'labels': [], 'Voltage': [], 'Current': []}

# @app.route('/api/update-dht-data', methods=['POST'])
# def update_dht_data():
#     global data_history

#     data = request.json
#     Voltage = data.get('Voltage')
#     Current = data.get('Current')

#     if Voltage is not None and Current is not None:
#         data_history['labels'].append(len(data_history['Voltage']))
#         data_history['Voltage'].append(Voltage)
#         data_history['Current'].append(Current)

#     return "Data received successfully!", 200

# @app.route('/')
# def index():
#     return render_template('Frontend.html')

# @app.route('/api/get-graph-data', methods=['GET'])
# def get_graph_data():
#     data = {"labels": data_history['labels'], "Voltage": data_history['Voltage'], "Current": data_history['Current']}
#     print("Data Received Successfully")
#     return jsonify(data)