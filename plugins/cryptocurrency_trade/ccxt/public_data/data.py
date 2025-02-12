import ccxt


from datetime import datetime
import time
import sys
import json
import os
import glob
import threading
from pprint import pprint


# print(os.getcwd())
sys.path.append(os.getcwd() + "/class/core")
import mw

# cd /www/server/mdserver-web && source bin/activate
# python3 plugins/cryptocurrency_trade/ccxt/public_data/data.py run
# python3 plugins/cryptocurrency_trade/ccxt/public_data/data.py long

# 查看支持的交易所
# print(ccxt.exchanges)

# 代理设置
# exchange = ccxt.poloniex({
#     'proxies': {
#         'http': 'http://127.0.0.1:1088'
#     },
# })

# exchange = ccxt.poloniex()
exchange = ccxt.okex()


def getPluginName():
    return 'cryptocurrency_trade'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getConfigData():
    cfg_path = getServerDir() + "/data.cfg"
    if not os.path.exists(cfg_path):
        mw.writeFile(cfg_path, '{}')
    t = mw.readFile(cfg_path)
    return json.loads(t)


def writeLog(log_str):
    if __name__ == "__main__":
        print(log_str)

    log_file = getServerDir() + '/logs/datasource.log'
    mw.writeFileLog(log_str, log_file, 1 * 1024 * 1024)
    return True


def isSetDbConf():
    data = getConfigData()
    if 'db' in data:
        return True
    return False


def beforeDate(day=360):
    dd = time.time() - day * 86400
    d = datetime.fromtimestamp(dd)
    day = d.strftime("%Y-%m-%d")
    return day


def getTextTimeShow(time):
    d = datetime.fromtimestamp(time)
    day = d.strftime("%Y-%m-%d %H:%M:%S")
    return day


def isSqlError(mysqlMsg):
    # 检测数据库执行错误
    mysqlMsg = str(mysqlMsg)
    if "MySQLdb" in mysqlMsg:
        return mw.returnJson(False, 'MySQLdb组件缺失! <br>进入SSH命令行输入: pip install mysql-python | pip install mysqlclient==2.0.3')
    if "2002," in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "2003," in mysqlMsg:
        return mw.returnJson(False, "Can't connect to MySQL server on '127.0.0.1' (61)")
    if "using password:" in mysqlMsg:
        return mw.returnJson(False, '数据库密码错误')
    if "1045" in mysqlMsg:
        return mw.returnJson(False, '连接错误!')
    if "SQL syntax" in mysqlMsg:
        return mw.returnJson(False, 'SQL语法错误!')
    if "Connection refused" in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "1133" in mysqlMsg:
        return mw.returnJson(False, '数据库用户不存在!')
    if "1007" in mysqlMsg:
        return mw.returnJson(False, '数据库已经存在!')
    return None


def pMysqlDb():
    # pymysql
    db = mw.getMyORM()
    data = getConfigData()
    db_data = data['db']
    db.setHost(db_data['db_host'])
    db.setPort(db_data['db_port'])
    db.setUser(db_data['db_user'])
    db.setPwd(db_data['db_pass'])
    db.setDbName(db_data['db_name'])
    return db


def makeInsertSql(table, item):
    sql = "insert into " + table
    keyStr = '('
    valueStr = ' values('
    for i in item:
        # print i, item[i]
        keyStr += '`' + str(i) + '`,'
        valueStr += "'" + str(item[i]) + "',"

    keyStrLen = len(keyStr)
    keyStr = keyStr[0:keyStrLen - 1]
    keyStr += ') '

    valueStrLen = len(valueStr)
    valueStr = valueStr[0:valueStrLen - 1]
    valueStr += ') '

    sql += keyStr
    sql += valueStr

    return sql


def makeReplaceSql(table, item):
    sql = "replace into " + table
    keyStr = '('
    valueStr = ' values('
    for i in item:
        # print i, item[i]
        keyStr += '`' + str(i) + '`,'
        valueStr += "'" + str(item[i]) + "',"

    keyStrLen = len(keyStr)
    keyStr = keyStr[0:keyStrLen - 1]
    keyStr += ') '

    valueStrLen = len(valueStr)
    valueStr = valueStr[0:valueStrLen - 1]
    valueStr += ') '

    sql += keyStr
    sql += valueStr

    return sql


def makeUpdateSql(table, item, mid):
    sql = "update " + table + " set "
    keyStr = ''
    for i in item:
        keyStr += '`' + str(i) + '`=' + "'" + item[i] + "',"

    keyStrLen = len(keyStr)
    keyStr = keyStr[0:keyStrLen - 1]
    sql += keyStr
    sql += " where id = '" + str(mid) + "'"
    return sql


def dataToDb(table_name, data):
    pdb = pMysqlDb()
    for i in data:
        rdata = {
            'addtime': int(i[0] / 1000),
            'open': i[1],
            'high': i[2],
            'low': i[3],
            'close': i[4],
            'vol': i[5],
        }

        # sql = """SELECT id FROM %s where addtime='%s' LIMIT 1""" % (
        #     table_name, rdata['addtime'])
        # fdata = pdb.query(sql)
        # if fdata:
        #     print(table_name + ":" + str(rdata['addtime']) + ", old to db ok")
        # else:
        #     isql = makeReplaceSql(table_name, rdata)
        #     r = pdb.execute(isql)
        #     print(table_name + ":" + str(rdata['addtime']) + ", go to db ok")

        isql = makeReplaceSql(table_name, rdata)
        r = pdb.execute(isql)
        # print(table_name + ":" + str(rdata['addtime']) + ", go to db ok")
    return True


def makeTableName(input_type="btc", input_tf="1m"):
    table_name = "ct_%s_%s" % (input_type, input_tf)
    return table_name


def isHasTable(input_type="btc", input_tf="1m"):
    pdb = pMysqlDb()

    # input_type = 'btc'
    # input_tf = '1m'
    table_name = makeTableName(input_type, input_tf)
    mtable = pdb.query("show tables like '%s'" % (table_name,))
    if len(mtable) != 0:
        return True
    return False


def createSql(input_type="btc", input_tf="1m"):
    pdb = pMysqlDb()

    # input_type = 'btc'
    # input_tf = '1m'
    table_name = makeTableName(input_type, input_tf)

    mtable = pdb.query("show tables like '%s'" % (table_name,))
    if len(mtable) != 0:
        return True

    sql_tpl = getPluginDir() + "/conf/create.sql"
    content = mw.readFile(sql_tpl)
    content = content.replace("xx1", input_type)
    content = content.replace("xx2", input_tf)

    res = pdb.execute(content)
    # pprint(res)
    return True


def getDataFetch(symbol,  start_time="2023-3-1", input_tf="1m", limit=500):
    start_time = datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.strptime(end_time, '%Y-%m-%d')

    start_time_stamp = int(time.mktime(start_time.timetuple())) * 1000
    data = exchange.fetch_ohlcv(symbol, timeframe=input_tf,
                                since=start_time_stamp, limit=limit)
    return data


def getPointData(symbol, start_time=1677713220000,  input_tf="1m", limit=500):
    data = exchange.fetch_ohlcv(
        symbol, timeframe=input_tf, since=start_time, limit=limit)
    return data


def toUnixTimeSecond(tf="1m"):
    if tf.find("m") > -1:
        v = int(tf.replace("m", ''))
        return v * 60

    if tf.find("h") > -1:
        v = int(tf.replace("h", ''))
        return v * 3600

    if tf.find("d") > -1:
        v = int(tf.replace("d", ''))
        return v * 86400
    return 0


def findAndUpdateData(tag, input_tf="1m", start_time="2023-1-1", limit=300):
    pdb = pMysqlDb()
    table_name = makeTableName(tag, input_tf)
    sql = 'SELECT addtime FROM ' + table_name + ' order by addtime desc LIMIT 1'
    qdata = pdb.query(sql)

    start_time = datetime.strptime(start_time, '%Y-%m-%d')
    start_time = int(time.mktime(start_time.timetuple())) * 1000
    if len(qdata) != 0:
        start_time = int(qdata[0]['addtime']) * 1000

    pre_time = toUnixTimeSecond(input_tf) * 5 * 1000
    start_time = start_time - pre_time
    # pprint(start_time)
    symbol = tag.upper() + "/USDT"
    data = getPointData(symbol,  start_time, input_tf, limit)

    # pprint(data)
    # print("------------lini===========")
    # pprint(data[1:])

    if len(qdata) == 1:
        data = data[1:]

    dataToDb(table_name, data)

    now = time.strftime("%m/%d %H:%M:%S")
    data_len = len(data)
    msg_head = now + "|虚拟币:" + tag + ",tf:" + \
        input_tf + "!,总数:" + str(data_len)
    writeLog(msg_head)
    if data_len > 0:
        # print("new data time", data[data_len - 1][0])
        dt = getTextTimeShow(data[data_len - 1][0] / 1000)
        msg = now + "|最新日期:" + dt
        writeLog(msg)

    table_name = makeTableName(tag, input_tf)

    sql = "SELECT addtime FROM " + table_name + \
        " order by addtime desc limit 10000,1"
    qdata = pdb.query(sql)

    if len(qdata) > 0:
        print(qdata)

        # input_tf_time = toUnixTimeSecond(input_tf)
        # now_t = int(time.time())

        # del_before_t = now_t - input_tf_time * 1000

        sql = "delete from %s where addtime<'%d' " % (
            table_name, qdata[0]['addtime'],)
        writeLog("删除冗余数据:" + str(sql))
        pdb.execute(sql)
    return True


def dataToDbTpl(tag='btc', input_tf="1m", start_time="2023-1-1", limit=300):
    # tag = "btc"
    # tf = "1m"
    # start_time = "2023-1-1"
    # end_time = "2023-3-2"
    symbol = tag.lower() + '/USDT'
    if not isHasTable(tag, input_tf):
        createSql(tag, input_tf)
        data = getDataFetch(symbol, start_time, input_tf, limit)
        table_name = makeTableName(tag, input_tf)

        dataToDb(table_name, data)
        now = time.strftime("%m/%d %H:%M:%S")
        data_len = len(data)
        writeLog(now + "|数据获取成功!,总数:" + str(data_len))
    else:
        findAndUpdateData(tag, input_tf, start_time, limit)

    return True


def dataToDbList(input_tf="1m", start_time="2023-1-1"):

    data = getConfigData()
    if not 'token' in data:
        writeLog("未设置同步配置,需要添加币种!")
        return

    for t in data['token']:
        dataToDbTpl(t, input_tf, start_time)
        time.sleep(4)


def dataRunToDb():
    data = getConfigData()
    if not 'db' in data:
        writeLog("数据库未设置!")
        return

    tag = "btc"
    symbol = tag.upper() + '/USDT'

    # pprint(exchange.fetch_ticker('XRP/USDT'))
    limit_count = 1
    start_time = "2023-1-1"
    end_time = "2023-3-2"
    tf = "1m"

    if not isHasTable(tag, tf):
        createSql(tag, tf)
        data = getDataFetch(symbol, start_time, end_time, tf, limit_count)
        table_name = makeTableName(tag, tf)

        dataToDb(table_name, data)
        china_datetime = str(datetime.now())
        data_len = len(data)
        writeLog(china_datetime + ":数据获取成功!,总数:" + str(data_len))
    else:
        findAndUpdateData(tag, tf, start_time, 30)
    return data


def startTask():
    # 任务队列
    try:
        while True:
            time.sleep(5)
    except Exception as e:
        time.sleep(60)
        startTask()


def setDaemon(t):
    if sys.version_info.major == 3 and sys.version_info.minor >= 10:
        t.daemon = True
    else:
        t.setDaemon(True)
    return t


def dataDay():
    try:
        while True:
            if not isSetDbConf():
                print("数据库未设置!")
            else:
                start_time = beforeDate(2 * 365)
                dataToDbList("1d", start_time=start_time)
            time.sleep(3600)
            # time.sleep(10)
    except Exception as e:
        time.sleep(60)
        dataDay()


def data4h():
    try:
        while True:
            if not isSetDbConf():
                print("数据库未设置!")
            else:
                start_time = beforeDate(365)
                dataToDbList("4h", start_time=start_time)
            time.sleep(10)
    except Exception as e:
        time.sleep(60)
        data4h()


def data1h():
    try:
        while True:
            if not isSetDbConf():
                print("数据库未设置!")
            else:
                start_time = beforeDate(365)
                dataToDbList("1h", start_time=start_time)
            time.sleep(10)
    except Exception as e:
        print(e)
        time.sleep(60)
        data1h()


def data15m():
    try:
        while True:
            if not isSetDbConf():
                print("数据库未设置!")
            else:
                start_time = beforeDate(365)
                dataToDbList("15m", start_time=start_time)
            time.sleep(10)
    except Exception as e:
        time.sleep(60)
        data15m()


def data5m():
    try:
        while True:
            if not isSetDbConf():
                print("数据库未设置!")
            else:
                start_time = beforeDate(180)
                dataToDbList("5m", start_time=start_time)
            time.sleep(10)
    except Exception as e:
        time.sleep(60)
        data5m()


def data1m():
    try:
        while True:
            if not isSetDbConf():
                print("数据库未设置!")
            else:
                start_time = beforeDate(30)
                dataToDbList("1m", start_time=start_time)
            time.sleep(10)
    except Exception as e:
        time.sleep(60)
        data1m()


def longRun():

    # 日线
    d1_tt = threading.Thread(target=dataDay)
    d1_tt = setDaemon(d1_tt)
    d1_tt.start()

    # 4h
    h4_tt = threading.Thread(target=data4h)
    h4_tt = setDaemon(h4_tt)
    h4_tt.start()

    # 1h
    h1_tt = threading.Thread(target=data1h)
    h1_tt = setDaemon(h1_tt)
    h1_tt.start()

    # 15m
    m15_tt = threading.Thread(target=data15m)
    m15_tt = setDaemon(m15_tt)
    m15_tt.start()

    # 5m
    m5_tt = threading.Thread(target=data5m)
    m5_tt = setDaemon(m5_tt)
    m5_tt.start()

    # 1m
    # h1m_tt = threading.Thread(target=data1m)
    # h1m_tt = setDaemon(h1m_tt)
    # h1m_tt.start()

    startTask()


def dataRun():
    do_num = 0
    while True:
        if do_num > 1:
            break
        do_num = do_num + 1
        dataRunToDb()
        time.sleep(6)

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'run':
        data5m()()
    elif func == 'long':
        longRun()
    elif func == 'demo':
        writeLog('111')
    else:
        print('error')
