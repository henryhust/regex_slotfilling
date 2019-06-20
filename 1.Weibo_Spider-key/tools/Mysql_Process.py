import pymysql as ps
import configparser


class mysqlHelper:
    def __init__(self, host, user, password, database, charset, port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.port = port
        self.db = None
        self.curs = None

    # 数据库连接
    def open(self):
        self.db = ps.connect(host=self.host, user=self.user, password=self.password, database=self.database,
                             charset=self.charset, port=self.port)
        self.curs = self.db.cursor()

    # 数据库关闭
    def close(self):
        self.curs.close()
        self.db.close()

    # 数据增删改
    def cud(self, sql, params):
        try:
            self.curs.execute(sql, params)
            # print("数据更新成功！\n")
        except Exception as err:
            print(err)

    #  提交操作
    def tijiao(self):
        try:
            self.db.commit()
            print("以上数据提交至数据库成功！\n")
        except Exception as err:
            print(err)
            self.db.rollback()

    # 数据查询
    def find(self, sql, params):
        self.open()
        try:
            result = self.curs.execute(sql, params)
            self.close()
            print("查询成功！\n")
            return result
        except:
            print('查询出现错误！\m')

        # 数据查询

    def findAll(self, sql, params):
        self.open()
        try:
            self.curs.execute(sql, params)
            # 获取所有记录列表
            result = self.curs.fetchall()
            self.close()
            # print("findAll数据操作调用成功！\n")
            return result
        except:
            print('查询出现错误！\n')


def get_db():
    conf = configparser.ConfigParser()
    conf.read("../tools/Config.cfg")
    db_host = conf.get("db", "db_host")
    db_user = conf.get("db", "db_user")
    db_password = conf.get("db", "db_password")
    db_database = conf.get("db", "db_database")
    db_charset = conf.get("db", "db_charset")
    db_port = conf.get("db", "db_port")
    db_config = [db_host, db_user, db_password, db_database, db_charset, db_port]
    return db_config
