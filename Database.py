import psycopg2
import constants

class Database(object):

    def __init__(self):

        self.cur = None
        self.conn = None
        self.host = constants.IP
        self.database = constants.DB
        self.user = constants.USER
        self.password = constants.PASSWORD

    def connect (self):

        print 'Initialize db connection: Start'
        self.conn = psycopg2.connect(
            host = self.host,
            database = self.database,
            user = self.user,
            password = self.password
        )
        self.cur = self.conn.cursor()
        print 'Initialize db connection: Done'

    def get_trace_idlist (self, kind_name):

        query = "SELECT id FROM trace WHERE kind = '"+kind_name+"'"
        self.cur.execute(query)
        idList = []
        while 1:
            one = self.cur.fetchone()
            if one:
                idList.append(one[0])
            else:
                # End of DataBase reached
                break
        return idList
