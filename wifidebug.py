import argparse
import sqlite3
import time

import matplotlib.pyplot as plt
from ping3 import ping


class PingDatabase:
    def __init__(self) -> None:
        self.connection = sqlite3.connect('ping_database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS pings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            recorded_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            latency INTEGER
        )''')
        self.connection.commit()

    def store_ping(self, ip: str, latency: int) -> None:
        self.cursor.execute('INSERT INTO pings (latency, ip) VALUES (?, ?)', (latency, ip))
        self.connection.commit()

    def read_pings(self, ip: str) -> tuple:
        self.cursor.execute('''SELECT ip, recorded_timestamp, latency
            FROM pings
            WHERE ip = ?
            ORDER BY recorded_timestamp DESC''', (ip,)
        )

        while True:
            row = self.cursor.fetchone()
            if row is None:
                break
            yield row

class Plotter:
    def __init__(self, db: PingDatabase) -> None:
        self.db = db

    def plot_pings(self, ip: str) -> None:
        pings = list(self.db.read_pings(ip))
        timestamps = [ping[1] for ping in pings]
        latencies = [ping[2] for ping in pings]

        plt.plot(timestamps, latencies)
        plt.xlabel('Time')
        plt.ylabel('Latency (ms)')
        plt.title('Ping latency over time')
        plt.show()

def main(ip: str, interval: int, quiet: bool = False):
    print("Will ping {} every {} milliseconds".format(ip, interval))

    db = PingDatabase()

    try:
        while True:
            latency = ping(ip, unit='ms')
            if not quiet: print("{} : {}ms".format(ip, latency))
            db.store_ping(ip, latency)
            time.sleep(interval / 1000)
    except KeyboardInterrupt:
        print('\nClosing connection...')
    finally:
        db.connection.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ping the given IP address and store the latency in an SQLite database.')
    parser.add_argument('ip', type=str, help='The IP address to ping.')
    parser.add_argument('--interval', type=int, help='Time to wait between pings, in ms.', default=1000, required=False)
    args = parser.parse_args()
    main(args.ip, args.interval)