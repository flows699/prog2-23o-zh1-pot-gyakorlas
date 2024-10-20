DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS reservations;

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_name TEXT NOT NULL UNIQUE,
    occupancy INTEGER DEFAULT 0
);

CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_name TEXT NOT NULL,
    day INTEGER NOT NULL DEFAULT "",
    reservation_start_time INTEGER NOT NULL DEFAULT "",
    reservation_end_time INTEGER NOT NULL DEFAULT "",
    event TEXT NOT NULL DEFAULT " ",
    FOREIGN KEY (room_name) REFERENCES rooms(room_name)
);