def GetCities():
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    c.execute("SELECT city FROM measuring_station")
    cit = c.fetchall()
    cities = list(set(cit))
    cities = sorted(cities, key=lambda x: (x[0]))
    cities_proper = []
    for i in cities:
        i = str(i[0])
        cities_proper.append(i)
    choice = []
    for i in range (0, len(cities_proper)):
        g = (cities_proper[i], cities_proper[i])
        choice.append(g)
    conn.close() 
    return choice
    

def GetStreets(x):
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT street FROM final WHERE city = ?;", tuple([x]))
    stree = c.fetchall()
    streets = []
    for i in range(0, len(stree)):
        streez = (stree[i][0],stree[i][0])
        streets.append(streez)
    conn.close()
    return streets


def GetPollutant1(x):
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    c.execute("SELECT paramName, paramCode FROM final WHERE street = ?;", tuple([x]))
    poll = c.fetchall()
    poll = list(set(poll))
    pollutants = []
    for i in range(0, len(poll)):
        pollz = (poll[i][1],poll[i][0])
        pollutants.append(pollz)
    if ("CO", "tlenek węgla") in pollutants:
        pollutants.remove(("CO", "tlenek węgla"))
    conn.close()
    return pollutants


def GetDate():
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    c.execute("SELECT date FROM final;")
    date = c.fetchall()
    date = list(set(date))
    date = sorted(date, key=lambda x: (x[0]))
    date_list = []
    for i in range(0, len(date)):
        datez = (date[i][0],date[i][0])
        date_list.append(datez)
    conn.close()
    return date_list


def GetTime():
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    c.execute("SELECT time FROM final;")
    time = c.fetchall()
    time = list(set(time))
    time = sorted(time, key=lambda x: (x[0]))
    time_list = []
    for i in range(0, len(time)):
        timez = (time[i][0],time[i][0])
        time_list.append(timez)
    conn.close()
    return time_list


def GetType(date):
    if date in ("Last 3 days", "Last 7 days"):
        types = [("Average", "Average")]
    else:
        types = [("Average", "Average"), ("Hourly","Hourly")]
    
    return types
