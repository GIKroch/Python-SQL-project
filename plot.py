def GetFinalData(city, street, paramCode, date, type):
    import matplotlib.pyplot as plt
    import sqlite3
    conn = sqlite3.connect('DB.db')
    c = conn.cursor()
    city = [city]
    paramCode = [paramCode]
    street = [street]
    date = date
    type = type

    c.execute("SELECT DISTINCT date FROM final;")
    dates = c.fetchall()
    dates = [x[0] for x in dates]
    dates.sort(reverse = True)


    try:
        if date == "Last 3 days":
            c.execute("""SELECT date, value FROM final WHERE (city = ?) and (Street = ?)
                    and (paramCode = ?) and date IN (?, ?, ?) """, (city + street + paramCode + dates[0:3]))
            FinalData = c.fetchall()
            FinalData.sort()
        elif date == "Last 7 days":
            c.execute("""SELECT date, value FROM final WHERE (city = ?) and (Street = ?)
                    and (paramCode = ?) and date IN  (?, ?, ?, ?, ?, ?, ?)""", (city + street + paramCode + dates[0:7]))
            FinalData = c.fetchall()
            FinalData.sort()
        else:
            c.execute("""SELECT time, value FROM final WHERE (city = ?) and (Street = ?)
                    and (paramCode = ?) and (date = ?)""",
                    (city + street + paramCode + [date]))
            FinalData = c.fetchall()
            FinalData.reverse()

        days_dict = dict()
        for x in FinalData:
            if x[0] in days_dict:
                days_dict[x[0]].append(x[1])
            else:
                days_dict[x[0]] = [x[1]]

        limits = {"C6H6": 5, "NO2": 40, "SO2": 20, "PM2.5": 25, "PM10": 40,
                "CO": 10000, "O3": 100}

        if type == "Average":
            average = []
            if date == "Last 3 days" or date == "Last 7 days":
                for k, v in days_dict.items():
                    x = sum(v)/len(v)
                    av = x
                    average.append(av)
                days = list(days_dict.keys())
                days = [day[5:] for day in days]
                fig = plt.figure()
                ax = plt.axes()
                ax.bar(days, average)
                ax.axhline(limits[paramCode[0]], linestyle = "--", color = "r")
                ax.text(0.8, limits[paramCode[0]] + 0.5, "Safe limit",
                        transform=ax.get_yaxis_transform())
                if max(average) > limits[paramCode[0]]:
                    ylimit = (0, max(average) + 10)
                else:
                    ylimit = (0, limits[paramCode[0]] + 10)
                ax.set(ylabel = 'Pollution level µg/m3',
                    ylim = ylimit,
                    title = "Average {} pollution in {} {}".format(paramCode[0],
                                                                    city[0],
                                                                    street[0]))
                for p in ax.patches:
                    ax.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=11, color='gray', xytext=(0, 20),
                        textcoords='offset points')
            else:
                values = []
                for k, v in days_dict.items():
                    values.append(v[0])
                values = sum(values)/len(values)
                values = [values]
                values.insert(0,0)
                days = ["-",date]
                fig = plt.figure()
                ax = plt.axes()
                ax.bar(days, values)
                ax.axhline(limits[paramCode[0]], linestyle = "--", color = "r")
                ax.text(0.8, limits[paramCode[0]] + 0.5, "Safe limit",
                        transform=ax.get_yaxis_transform())
                if max(values) > limits[paramCode[0]]:
                    ylimit = (0, max(values) + 10)
                else:
                    ylimit = (0, limits[paramCode[0]] + 10)
                ax.set(xlim = (0,2), ylabel = 'Pollution level µg/m3',
                    ylim = ylimit,
                    title = "Average {} pollution in {} {}".format(paramCode[0],
                                                                    city[0],
                                                                    street[0]))
                for p in ax.patches:
                    ax.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=11, color='gray', xytext=(0, 20),
                        textcoords='offset points')
            error = None
            plt.savefig('static/images/newplot.png')

        else:
            hours = []
            values = []
            for k, v in days_dict.items():
                k = k[0:2]
                v = v[0]
                hours.append(k)
                values.append(v)
            fig = plt.figure()
            ax = plt.axes()
            ax.plot(hours, values)
            ax.axhline(limits[paramCode[0]], linestyle = "--", color = "r")
            ax.axvline(x = (int((max(days_dict, key=days_dict.get)[0:2]))),
                    linestyle = ":", color = "grey")
            ax.axvline(x = (int((min(days_dict, key=days_dict.get)[0:2]))),
                    linestyle = ":", color = "grey")
            ax.text(0.8, limits[paramCode[0]] + 0.5, "Safe limit",
                    transform=ax.get_yaxis_transform())
            ax.set(xticks = (ax.get_xticks()[::2]), ylabel = 'Pollution level µg/m3',
                   title = "Hourly {} pollution in {} {}".format(paramCode[0],
                                                                city[0],
                                                                street[0]))
            if max(values) > limits[paramCode[0]]:
                ylimit = (0, max(values) + 0.2 * max(values))
            else:
                ylimit = (0, limits[paramCode[0]] + 0.2 * max(values))

            ax.set(xticks = (ax.get_xticks()[::2]), ylabel = 'Pollution level µg/m3',
                ylim =  ylimit,
                title = "Hourly {} pollution in {} {}".format(paramCode[0],
                                                            city[0],
                                                            street[0]))


            ax.annotate(round(max(values),2),
                        xy = (int((max(days_dict, key=days_dict.get)[0:2])),
                        max(values)), xytext = (int((max(days_dict,
                        key=days_dict.get)[0:2])), max(values) + 0.15 * max(values)),
                        arrowprops=dict(facecolor='black', shrink=0.05))
            ax.annotate(round(min(values),2),
                        xy = (int((min(days_dict, key=days_dict.get)[0:2])),
                        min(values)), xytext = (int((min(days_dict,
                        key=days_dict.get)[0:2])), min(values) + 0.15 * max(values)),
                        arrowprops=dict(facecolor='black', shrink=0.05))
            plt.savefig('static/images/newplot.png')
            error  = None
    except:
        error = [("""You have not provided a choice for all required choice fields (or the data for your choices might not be available). 
                  Go back and fill all the fields or choose another options""")]

    return error
