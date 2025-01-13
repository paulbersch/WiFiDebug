from wifidebug import PingDatabase

db = PingDatabase()

for ping in db.read_pings("8.8.4.4"):
    print(ping)



