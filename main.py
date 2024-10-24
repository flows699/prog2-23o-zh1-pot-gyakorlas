from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import matplotlib.pyplot as plt
import os
import threading
import matplotlib

app = Flask(__name__)
DATABASE = "db.sqlite"
matplotlib.use('Agg') #ne használjon grafikus megjelenítést


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DATABASE, detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def main_page():
    return render_template("base.html")

@app.route("/rooms", methods=["GET", "POST"])
def show_rooms():
    if request.method == "POST":
        db = get_db()
        db.execute("INSERT INTO rooms (room_name, occupancy) VALUES (?, ?)", (request.form["name"], 0))
        db.commit()

        return redirect(url_for('show_rooms'))
    
    db = get_db()
    rooms = db.execute("SELECT * FROM rooms").fetchall()

    def create_plot():
        plt.bar([room["room_name"] for room in rooms], [room["occupancy"] for room in rooms])
        plt.xlabel("Rooms")
        plt.ylabel("Occupancy")
        os.makedirs("static", exist_ok=True)
        plt.savefig("static/occupancy.png")
        plt.close()

    threading.Thread(target=create_plot).start()

    return render_template("rooms.html", rooms=rooms)

@app.route("/reserve/<room_name>", methods=["GET", "POST"])
def get_room(room_name):
    if request.method == "POST":
        db = get_db()
        event_name = request.form["event_name"]
        day = request.form['day']
        start_time = int(request.form['start_time'])
        end_time = int(request.form['end_time'])

        if start_time >= end_time:
            return "End time must be greater than start time", 400

        all_reservations_day = db.execute("SELECT reservation_start_time, reservation_end_time FROM reservations WHERE room_name = ? AND day = ?", (room_name, day)).fetchall()

        for reservation in all_reservations_day:
            for hour in range(reservation["reservation_start_time"], reservation["reservation_end_time"]):
                if start_time <= hour < end_time: 
                    return "Time already reserved", 400
        

        db.execute("INSERT INTO reservations (room_name, day, reservation_start_time, reservation_end_time, event) VALUES (?, ?, ?, ?, ?)", 
                   (room_name, day, start_time, end_time, event_name))
        hours = end_time - start_time
        db.execute("UPDATE rooms SET occupancy = occupancy + ? WHERE room_name = ?", (hours, room_name,))
        db.commit()

        return redirect(url_for('get_room', room_name=room_name))

    db = get_db()
    room = db.execute("SELECT * FROM rooms WHERE room_name = ?", (room_name,)).fetchone()
    reservations = db.execute("SELECT * FROM reservations WHERE room_name = ?", (room_name,)).fetchall()
    
    reservations_matrix = [["" for _ in range(24)] for _ in range(5)]
    
    for reservation in reservations:
        day = reservation["day"]
        start_hour = reservation["reservation_start_time"]
        event = reservation["event"]
        
        for hour in range(start_hour, reservation["reservation_end_time"]):
            reservations_matrix[day][hour] = event

    return render_template("room.html", room=room, reservations=reservations_matrix)


@app.route("/rooms/clear", methods=["POST"])
def clear_reservations():
    db = get_db()
    db.execute("DELETE FROM reservations")
    db.execute("UPDATE rooms SET occupancy = 0")
    db.commit()

    return redirect(url_for('show_rooms'))


if __name__ == "__main__":
    app.teardown_appcontext(close_db)
    app.run(debug=True)