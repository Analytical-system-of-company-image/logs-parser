class LogStruct:
    '''class log nginx or apache server structure'''

    def __getmonths(self, monthname):
        '''return number of month'''
        months = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sept": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }
        return months[monthname]

    def __formatdate(self, datetime):
        '''return list with parsed time,zone,date'''
        slash = datetime.find('/')
        day = datetime[:slash]
        datetime = datetime[slash + 1:]
        slash = datetime.find('/')
        month = datetime[:slash]
        datetime = datetime[slash + 1:]
        month = self.__getmonths(month)
        twopoint = datetime.find(':')
        year = datetime[:twopoint]
        datetime = datetime[twopoint + 1:]
        space = datetime.find(' ')
        time = datetime[: space]
        zone = int(datetime[space + 1:])
        date = year + '-' + month + '-' + day
        return [time, zone, date]

    def __init__(self, ip, user, datetime, request, response, bytesSent, referer, browser):
        self.ip = ip
        self.user = user
        self.request = request
        self.response = response
        self.bytesSent = bytesSent
        self.referer = referer
        self.browser = browser
        resdatetime = self.__formatdate(datetime)
        self.time = resdatetime[0]
        self.zone = resdatetime[1]
        self.date = resdatetime[2]

    def __len__(self):
        return 10

    def __getitem__(self, item):
        nowlist = []
        nowlist.append(self.ip)
        nowlist.append(self.user)
        nowlist.append(self.date)
        nowlist.append(self.time)
        nowlist.append(self.zone)
        nowlist.append(self.request)
        nowlist.append(self.response)
        nowlist.append(self.bytesSent)
        nowlist.append(self.referer)
        nowlist.append(self.browser)

        return nowlist[item]

    def __str__(self):
        delim = '|'
        return "{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}{0}{8}{0}{9}{0}{10}\n".format(delim, self.ip, self.user,
                                                                                     self.date,
                                                                                     self.time, self.zone,
                                                                                     self.request, self.response,
                                                                                     self.bytesSent,
                                                                                     self.referer, self.browser)
