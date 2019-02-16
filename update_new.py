def UpdateDB():
    import sqlite3
    import datetime
    import json
    import requests
    import rewriting

    conn = sqlite3.connect("DB.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT date FROM final")
    dates = c.fetchall()
    dates = [x[0] for x in dates]
    dates.sort(reverse = True)
    today = datetime.date.today()
    day = datetime.timedelta(days=1)
    yesterday = today - day
    yesterday = str(yesterday)
    
    c.execute("DROP TABLE IF EXISTS pollution_stats;")
    conn.commit()

    if yesterday not in dates:
        url = 'http://api.gios.gov.pl/pjp-api/rest/data/getData/'
        url_all = rewriting.API_multiplication("SELECT sensorID FROM sensors_data", url)
        list_1 = []
        for u in range(0, len(url_all)):
            try:
                r = requests.get(url_all[u])
                jason = json.loads(r.text)
                jason["url"] = url_all[u] 
                list_1.append(jason)
            except:
                continue

        final_stats = []
        for i in range(0,len(list_1)):
            for z in range(0, len(list_1[i]["values"])):
                stat = [list_1[i]["url"][len(url):len(list_1[i]["url"])],
                        list_1[i]["key"], 
                        str.split(list_1[i]["values"][z]["date"])[0],
                        str.split(list_1[i]["values"][z]["date"])[1],
                        list_1[i]["values"][z]["value"]]
                if stat[4] != None:
                    final_stats.append(stat)


        conn = sqlite3.connect("DB.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE pollution_stats (sensorID INTEGER,
                        paramCode VARCHAR (8),
                        date DATE, time TIME, 
                        value INTEGER, 
                        FOREIGN KEY(sensorID) REFERENCES sensors_data(sensorID))""")


        c.executemany("INSERT INTO pollution_stats VALUES (?, ?, ?, ?, ?);",
                    final_stats)
        conn.commit()
    else:
        c.execute("""CREATE TABLE pollution_stats (sensorID INTEGER,
                  paramCode VARCHAR (8),
                  date DATE, time TIME, value INTEGER, FOREIGN KEY(sensorID) REFERENCES sensors_data(sensorID))""")
        conn.commit()

    c.execute("SELECT DISTINCT date FROM final;")
    date_check = c.fetchall()
    date_check.sort()
    if len(date_check) > 30:
        c.execute("DELETE FROM final WHERE date = ?", date_check[0])
        conn.commit()

    
    conn.close()
