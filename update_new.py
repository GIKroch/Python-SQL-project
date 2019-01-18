def UpdateDB():
    import sqlite3
    import datetime
    import json
    import requests
    conn = sqlite3.connect("FinalDB.db")
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
        #### x is a string choosing proper column from SQL DB.
        #### The column contains IDs,
        #### which we can add to URL to get data for specified ID
        idd = []
        for row in c.execute("SELECT sensorID FROM sensors_data"):
            idd.append(row)
        idd = [i[0] for i in idd]

        #### url is a string representing url adrress which will
        #### be modified in every iterration
        url = 'http://api.gios.gov.pl/pjp-api/rest/data/getData/'
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

        final_stats = []
        list_1 = []
        for u in range(0, len(url_all)):
            try:
                r = requests.get(url_all[u])
                jason = json.loads(r.text)
                jason["url"] = url_all[u]
                list_1.append(jason)
            except:
                continue

        for i in range(0,len(list_1)):
            for z in range(0, len(list_1[i]["values"])):
                stat = [list_1[i]["url"][len(url):len(list_1[i]["url"])],
                        list_1[i]["key"], list_1[i]["values"][z]["date"],
                        str.split(list_1[i]["values"][z]["date"])[0],
                        str.split(list_1[i]["values"][z]["date"])[1],
                        list_1[i]["values"][z]["value"]]
                if stat[5] != None:
                    final_stats.append(stat)
        final_list = []

        for i in range(0, len(final_stats)):
            final_stats[i][0] = int(final_stats[i][0])

        for i in range(0, len(final_stats)):
            if final_stats[i][3] == yesterday:
                final_list.append(final_stats[i])

        c.execute("""CREATE TABLE pollution_stats (sensorID INTEGER,
                  paramCode VARCHAR (8), datetime DATETIME,
                  date DATE, time TIME, value INTEGER, FOREIGN KEY(sensorID) REFERENCES sensors_data(sensorID))""")
        conn.commit()

        c.executemany("INSERT INTO pollution_stats VALUES (?, ?, ?, ?, ?, ?);",
                      final_list)
        conn.commit()
    else:
        c.execute("""CREATE TABLE pollution_stats (sensorID INTEGER,
                  paramCode VARCHAR (8), datetime DATETIME,
                  date DATE, time TIME, value INTEGER, FOREIGN KEY(sensorID) REFERENCES sensors_data(sensorID))""")
        conn.commit()

    c.execute("SELECT DISTINCT date FROM final;")
    date_check = c.fetchall()
    date_check.sort()
    if len(date_check) > 30:
        c.execute("DELETE FROM final WHERE date = ?", date_check[0])
        conn.commit()

    
    conn.close()
