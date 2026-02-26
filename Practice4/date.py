import datetime

today = datetime.datetime.now()
five = today - datetime.timedelta(days=5)
print("five days ago:", five)

yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)
print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)

nomicro = today.replace(microsecond=0)
print("no microseconds:", nomicro)

date1 = datetime.datetime(2026, 1, 1)
date2 = datetime.datetime(2026, 6, 15)
difference = date2 - date1
print(difference.total_seconds())