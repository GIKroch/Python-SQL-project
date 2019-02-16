def connect_jason(url):
    import json
    import requests
    r = requests.get(url)
    jason = json.loads(r.text)
    return jason

def API_multiplication(sql_command, part_url):
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    idd = []
    for row in c.execute(sql_command):
        idd.append(row)
    idd = [i[0] for i in idd]

    url = part_url
    url_list = []
    for i in url:
        url_list.append(i)

    url_all = []
    i = 0
    while i < len(idd):
        g = url_list + [idd[i]]
        url_all.append(g)
        i += 1

    for i in range(0, len(url_all)):
        url_all[i] = ''.join(map(str, url_all[i]))
        
    return url_all

def MeasuringStation():
    url = 'http://api.gios.gov.pl/pjp-api/rest/station/findAll'
    jason = connect_jason(url)
    
    stations = []
    for i in jason:
        stations.append((i["id"],i["city"]["name"],i["addressStreet"]))
    
    stations_final = []
    for i in stations:
        if i[1] in ["Wrocław", "Kraków", "Warszawa", 
                     "Poznań", "Łódź", "Gdańsk"]:
            stations_final.append(i)
    
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE measuring_station (stationID INTEGER PRIMARY KEY,
              City VARCHAR (32), Street VARCHAR (50))""")
    c.executemany("INSERT INTO measuring_station VALUES (?, ?, ?);", stations_final)
    conn.commit()
    conn.close()

def SensorsID():
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    
    idd = []
    for row in c.execute("SELECT stationID FROM measuring_station"):
        idd.append(row)
    idd = [i[0] for i in idd]

    url = "http://api.gios.gov.pl/pjp-api/rest/station/sensors/"
    url_list = []
    for i in url:
        url_list.append(i)

    url_all = []
    i = 0
    while i < len(idd):
        g = url_list + [idd[i]]
        url_all.append(g)
        i += 1

    for i in range(0, len(url_all)):
        url_all[i] = ''.join(map(str, url_all[i]))

    sensors = []
    for i in range(0, len(url_all)):
        jason = connect_jason(url_all[i])
        sensors.append(jason)
    
    sensors = [subitem for item in sensors for subitem in item]
    
    sensors_id = []
    for i in sensors:
        sensors_id.append((i["id"], i["stationId"], i["param"]["paramName"], i["param"]["paramCode"]))

    c.execute("""CREATE TABLE sensors_data (sensorID INT PRIMARY KEY,
              stationID INT, paramName VARCHAR(30), paramCode VARCHAR(8), 
              FOREIGN KEY(stationID) REFERENCES measuring_station(stationID));""")
    c.executemany("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", sensors_id)
    conn.commit()
    conn.close()



def FinalStats():
    import sqlite3
    import update_new
    
    update_new.UpdateDB()
    conn = sqlite3.connect("DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM pollution_stats")
    poll = c.fetchall()
    if len(poll) == 0:
        pass
    else:
        c.execute("""SELECT measuring_station.City, measuring_station.Street,
                  sensors_data.stationID, pollution_stats.sensorID,
                  sensors_data.paramName, sensors_data.paramCode,
                  pollution_stats.date, pollution_stats.time,
                  pollution_stats.value
                  FROM pollution_stats
                  JOIN sensors_data ON
                  pollution_stats.sensorID = sensors_data.sensorID
                  JOIN measuring_station ON
                  sensors_data.stationID = measuring_station.stationID""")
        zz = c.fetchall()
        # c.execute("""CREATE TABLE final (City VARCHAR(32), Street VARCHAR(40),
        #                                  stationID INT, sensorID INT,
        #                                  paramName VARCHAR(40), paramCode VARCHAR(8),
        #                                  date DATE, time TIME, value INT,
        #                                  FOREIGN KEY(stationID) REFERENCES measuring_station(stationID), 
        #                                  FOREIGN KEY(sensorID) REFERENCES sensors_data(sensorID))""")
        c.executemany("INSERT INTO final VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", zz)
        conn.commit()

    bug_streets = c.execute("""SELECT DISTINCT street FROM final WHERE street LIKE "%/%";""")
    bug_streets = list(bug_streets)
    bug_streets = [x[0] for x in bug_streets]

    bugfix = bug_streets.copy()
    ind = []
    for h in bugfix:
        ind.append(h.index("/"))
    for h in range(0, len(bugfix)):
        bugfix[h] = bugfix[h][:ind[h]]

    for i in range(0, len(bugfix)):
        c.execute("UPDATE final SET street = ? WHERE street = ?", (bugfix[i], bug_streets[i]))
        conn.commit()
    
    conn.close()
    
    
