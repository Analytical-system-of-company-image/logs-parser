from typing import Any, Dict, Tuple


class LogStruct:
    '''class log nginx or apache server structure'''

    def __get_months(self, monthname: str) -> str:
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

    def __format_date(self, datetime: str) -> Tuple[str, int, str]:
        '''return list with parsed time,zone,date'''
        slash = datetime.find('/')
        day = datetime[:slash]
        datetime = datetime[slash + 1:]
        slash = datetime.find('/')
        month = datetime[:slash]
        datetime = datetime[slash + 1:]
        month = self.__get_months(month)
        twopoint = datetime.find(':')
        year = datetime[:twopoint]
        datetime = datetime[twopoint + 1:]
        space = datetime.find(' ')
        time = datetime[: space]
        zone = int(datetime[space + 1:])
        date = year + '-' + month + '-' + day
        return [time, zone, date]

    def __init__(self, ip: str, user: str, datetime: str,
                 request: str, response: str, bytes_sent: str, referrer: str,
                 browser: str) -> None:
        self.ip_address: str = ip
        self.user: str = user
        self.request: str = request
        self.response: str = response
        self.bytes_sent: str = bytes_sent
        self.referrer: str = referrer
        self.browser: str = browser
        res_date_time: Tuple = self.__format_date(datetime)
        self.time: str = res_date_time[0]
        self.zone: int = res_date_time[1]
        self.date: str = res_date_time[2]

    def __len__(self) -> int:
        ":return num of fields of structure"
        return 10

    def __getitem__(self, item):
        nowlist = []
        nowlist.append(self.ip_address)
        nowlist.append(self.user)
        nowlist.append(self.date)
        nowlist.append(self.time)
        nowlist.append(self.zone)
        nowlist.append(self.request)
        nowlist.append(self.response)
        nowlist.append(self.bytes_sent)
        nowlist.append(self.referrer)
        nowlist.append(self.browser)

        return nowlist[item]

    def asdict(self) -> Dict[str, Any]:
        """Get as dict

        Returns:
            Dict[str,Any]:
        """
        return {"id_address": self.ip_address,
                "user": self.user,
                "request": self.request,
                "response": self.response,
                "bytes_sent": self.bytes_sent,
                "referrer": self.referrer,
                "browser": self.browser,
                "time": self.time,
                "zone": self.zone,
                "date": self.date}

    def __str__(self):
        return f"{self.ip_address}|{self.user}|{self.date}|{self.time}|{self.zone}|" \
               f"{self.request}|{self.response}|{self.bytes_sent}|{self.referrer}|{self.browser}\n"
