def MeasuringStation():
    import json
    import requests
    url = 'http://api.gios.gov.pl/pjp-api/rest/station/findAll'
    r = requests.get(url)
    jason = json.loads(r.text)

    #### simplifying jason, putting it into a list
    z = []
    measure = []
    i = 0
    while i < len(jason):
        z.clear()
        for k, v in jason[i].items():
            z.append(v)
        measure.append(z.copy())
        i += 1
    #### measure list has a dictionary inside, so [i][4][name]
    #### unpacks this dictionary
    #### two other elements just get what is important for db
    stations = []
    for i in range(0, len(measure)):
        station = [measure[i][0], measure[i][4]["name"], measure[i][5]]
        stations.append(station)
    #### there are some stations with no street's name
    #### instead, here I assign the name of the city
    for i in range (0, len(stations)):
        if stations[i][2] == None:
            stations[i][2] = stations[i][1]

    import sqlite3
    conn = sqlite3.connect('FinalDB.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE measuring_station (stationID INTEGER PRIMARY KEY,
              City VARCHAR (32), Street VARCHAR (50))""")
    c.executemany("INSERT INTO measuring_station VALUES (?, ?, ?);", stations)
    conn.commit()
    conn.close()


def SensorsID():

    import sqlite3
    conn = sqlite3.connect('FinalDB.db')
    c = conn.cursor()
    idd = []
    for row in c.execute("SELECT stationID FROM measuring_station"):
        idd.append(row)
    idd = [i[0] for i in idd]

    #### turning the string into the list to be able to add to the end of
    #### the string stations' ids. The whole api is
    #### http://api.gios.gov.pl/pjp-api/rest/station/sensors/station_ID
    #### every url is placed in separated list
    #### every letter of the url becomes this list element.
    url = "http://api.gios.gov.pl/pjp-api/rest/station/sensors/"
    url_list = []
    for i in url:
        url_list.append(i)

    #### assigning ids to the lists of urls
    url_all = []
    i = 0
    while i < len(idd):
        g = url_list + [idd[i]]
        url_all.append(g)
        i += 1

    #### joining strings to get final urls
    for i in range(0, len(url_all)):
        url_all[i] = ''.join(map(str, url_all[i]))

    #### saving json to a list
    import json
    import requests
    sensors = []
    for i in range(0, len(url_all)):
        urll = url_all[i]
        r = requests.get(urll)
        jason = json.loads(r.text)
        sensors.append(jason)

    #### Getting rid of nested list so to have list of dictionaries, not
    #### list of lists of dictionaries
    new_sensors = []
    for i in range(0, len(sensors)):
        for x in sensors[i]:
            new_sensors.append(x)

    #### unpacking list of dictionaries into a list
    #### which can be passed into the database
    final_sensors = []
    for i in range(0, len(sensors)):
        for z in range(0, len(sensors[i])):
            sensor = [sensors[i][z]["id"], sensors[i][z]["stationId"],
                      sensors[i][z]["param"]["paramName"],
                      sensors[i][z]["param"]["paramCode"]]
            final_sensors.append(sensor)

    c.execute("""CREATE TABLE sensors_data (sensorID INT PRIMARY KEY,
              stationID INT, paramName VARCHAR(30), paramCode VARCHAR(8), 
              FOREIGN KEY(stationID) REFERENCES measuring_station(stationID));""")
    c.executemany("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", final_sensors)
    conn.commit()
    conn.close()


def FinalStats():
    import sqlite3
    import update_new
    
    update_new.UpdateDB()
    conn = sqlite3.connect("FinalDB.db")
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
    
    
