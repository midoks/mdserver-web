import time

from datetime import datetime
china_datetime = datetime.now()
print(china_datetime)


# date()
tt = time.time() - 180 * 86400

# print(date("%Y-%m-%d", time.time()))
# t = datetime.strptime(str(time.time() - 180 * 86400), "%Y-%m-%d")
# print(t)


d = datetime.fromtimestamp(tt)
# 精确到毫秒
str1 = d.strftime("%Y-%m-%d")
print(str1)
