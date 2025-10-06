import pymysql.cursors

class MySQLConnection:
    def __init__(self, db):
        try:
            self.connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database=db,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
        except Exception as e:
            print("Error al conectar con MySQL:", e)

    def query_db(self, query, data=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, data)
                if query.lower().startswith('select'):
                    return cursor.fetchall()
                self.connection.commit()
                return cursor.lastrowid
        except Exception as e:
            print("Error en query:", e)
            return None

def connectToMySQL(db):
    return MySQLConnection(db)
