import sqlite3
import hashlib
import datetime

db = 'db_files/conftracker.db'

class Schema:
    def __init__(self):
        self.conn = sqlite3.connect(db)
        self.create_conf_table()
        self.create_record_table()
        self.create_user_table()

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()   

    def create_conf_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Confs" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            abbr char(64) NOT NULL,
            title varchar(128) NOT NULL,
            category varchar(64) DEFAULT NULL,
            publisher char(64) DEFAULT NULL,
            hindex int(4) DEFAULT -1,
            ccfrank char(1) DEFAULT NULL,
            irank char(2) DEFAULT NULL,
            create_time timestamp DEFAULT CURRENT_TIMESTAMP
        );
        """

        # UserId INTEGER FOREIGNKEY REFERENCES User(_id)
        self.conn.execute(query)

    def create_record_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Records" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER FOREIGNKEY REFERENCES User(id),
            abbr char(64) NOT NULL,
            title varchar(128) NOT NULL,
            category varchar(64) DEFAULT NULL,
            publisher char(64) DEFAULT NULL,
            hindex int(4) DEFAULT -1,
            ccfrank char(1) DEFAULT NULL,
            irank char(2) DEFAULT NULL,
            year int(4) NOT NULL,
            startdate date DEFAULT NULL,
            enddate date DEFAULT NULL,
            absdate date DEFAULT NULL,
            subdate date DEFAULT NULL,
            notifdate date DEFAULT NULL,
            crdate date DEFAULT NULL,
            city varchar(35) DEFAULT NULL,
            country varchar(35) DEFAULT NULL,
            link varchar(256) DEFAULT NULL,
            subno int(11) DEFAULT NULL,
            acceptno int(11) DEFAULT NULL,
            acceptrate int(11) DEFAULT NULL,
            confirmed boolean DEFAULT 0,
            subscribers char(128) DEFAULT NULL,
            update_time timestamp DEFAULT CURRENT_TIMESTAMP,
            create_time timestamp DEFAULT CURRENT_TIMESTAMP
        );
        """

        self.conn.execute(query)

    def create_user_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Users" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name char(64) NOT NULL,
            last_name char(64) NOT NULL,
            email char(128) NOT NULL,
            homepage varchar(256) DEFAULT NULL,
            affiliation char(128) DEFAULT NULL,
            create_time timestamp DEFAULT CURRENT_TIMESTAMP
        );
        """

        self.conn.execute(query)

class Conf:
    TABLENAME = "Confs"
    def __init__(self):
        self.conn = sqlite3.connect(db)

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()  

    def get_items(self, query_arg = ''):
        # query = """
        #     SELECT * FROM Confs;
        # """
        query = "SELECT * FROM " + self.TABLENAME + " WHERE " + query_arg
        ret = self.conn.execute(query)
        return ret

    def create(self, conf):
        # query = f'insert into {self.TABLENAME} ' \
        #         f'(Name, Email) ' \
        #         f'values ({name},{email})'
        data = [conf['abbr'], conf['title'], conf['category'], conf['publisher'], conf['hindex'], conf['ccfrank'], conf['irank']]
        query = 'insert into ' + self.TABLENAME + '(abbr, title, category, publisher, hindex, ccfrank, irank) ' \
                + 'values (' + ','.join(data) +')'
        result = self.conn.execute(query)
        return result

class Record:
    TABLENAME = "Records"
    def __init__(self):
        self.conn = sqlite3.connect(db)

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    def get_items(self):
        return get_items(query_args = 'True', sort='subdate')

    def get_items(self, query_args, sort):
        # query = """
        #     SELECT * FROM Confs;
        # """
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        # conn.text_factory = str
        query = "SELECT * FROM " + self.TABLENAME + " WHERE " + query_args + " ORDER BY " + sort + " DESC"
        cursor = conn.execute(query)
        # print(query)        
        results = [dict(row) for row in cursor.fetchall()]
        conn.commit()
        conn.close()
        return results

    def get_item(self, conf_id):
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        conn.text_factory = str
        query = "SELECT * FROM " + self.TABLENAME + " WHERE id=" + conf_id
        results = conn.execute(query).fetchone()
        if results:
            results = dict(results)
        conn.commit()
        conn.close()
        return results


    def create(self, conf):
        conn = sqlite3.connect(db)
        data = [conf['uid'], conf['abbr'], conf['title'], conf['year'], conf['category'], conf['publisher'], conf['ccfrank'], conf['link'], conf['city'], conf['country'], conf['startdate'], conf['enddate'], conf['absdate'], conf['subdate'], conf['notifdate'], conf['crdate']]
        data = ', '.join("'{0}'".format(w) for w in data)        
        query = 'insert into ' + self.TABLENAME + ' (uid, abbr, title, year, category, publisher, ccfrank, link, city, country, startdate, enddate, absdate, subdate, notifdate, crdate) ' \
                + 'values (' + data +')'
        # print(query)
        result = conn.execute(query)
        conn.commit()
        conn.close()
        return result

    def update(self, conf):
        conn = sqlite3.connect(db)
        # data = [conf['abbr'], conf['title'], conf['year'], conf['category'], conf['publisher'], conf['ccfrank'], conf['link'], conf['city'], conf['country'], conf['startdate'], conf['enddate'], conf['absdate'], conf['subdate'], conf['notifdate'], conf['crdate']]
        # data = ', '.join("'{0}'".format(w) for w in data) 
        # print(data)       
        query = 'UPDATE ' + self.TABLENAME + ' SET abbr=?, title=?, year=?, category=?, publisher=?, ccfrank=?, ' \
            'link=?, city=?, country=?, startdate=?, enddate=?, absdate=?, subdate=?, notifdate=?, crdate=? ' \
                + ' WHERE id=?'
        # print(query)
        result = conn.execute(query, (conf['abbr'], conf['title'], conf['year'], conf['category'], 
                    conf['publisher'], conf['ccfrank'], conf['link'], conf['city'], conf['country'], 
                    conf['startdate'], conf['enddate'], conf['absdate'], conf['subdate'], 
                    conf['notifdate'], conf['crdate'], conf['id']))
        conn.commit()
        conn.close()
        return result

    def subscribe(self, conf, user):
        status = -1
        user = str(user)
        conn = sqlite3.connect(db)
        conn.text_factory = str
        query = "SELECT subscribers FROM " + self.TABLENAME + " WHERE id=" + str(conf)
        subscribe = conn.execute(query).fetchone()
        if not subscribe:
            print('No record with conf id ', conf)
            return status
        subscribe = subscribe[0]
        if not subscribe:
            subscribe = ',' + user + ','
            status = 1
        elif ',' + user + ',' not in subscribe:
            subscribe += user + ','
            status = 1
        else:
            subscribe = subscribe.replace(","+user+",", ",")
            status = 0
        query = "UPDATE " + self.TABLENAME + " SET subscribers='" + subscribe + "' WHERE id=" + str(conf)
        # print(query)
        result = conn.execute(query)

        conn.commit()
        conn.close()
        return status

class ToDoModel:
    TABLENAME = "Todo"

    def __init__(self):
        self.conn = sqlite3.connect('todo.db')
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    # def get_by_id(self, _id):
    #     where_clause = f"AND id={_id}"
    #     return self.list_items(where_clause)

    # def create(self, params):
    #     print (params)
    #     query = f'insert into {self.TABLENAME} ' \
    #             f'(Title, Description, DueDate, UserId) ' \
    #             f'values ("{params.get("Title")}","{params.get("Description")}",' \
    #             f'"{params.get("DueDate")}","{params.get("UserId")}")'
    #     result = self.conn.execute(query)
    #     return self.get_by_id(result.lastrowid)

    # def delete(self, item_id):
    #     query = f"UPDATE {self.TABLENAME} " \
    #             f"SET _is_deleted =  {1} " \
    #             f"WHERE id = {item_id}"
    #     print (query)
    #     self.conn.execute(query)
    #     return self.list_items()

    # def update(self, item_id, update_dict):
    #     """
    #     column: value
    #     Title: new title
    #     """
    #     set_query = ", ".join([f'{column} = {value}'
    #                  for column, value in update_dict.items()])

    #     query = f"UPDATE {self.TABLENAME} " \
    #             f"SET {set_query} " \
    #             f"WHERE id = {item_id}"
    #     self.conn.execute(query)
    #     return self.get_by_id(item_id)

    # def list_items(self, where_clause=""):
    #     query = f"SELECT id, Title, Description, DueDate, _is_done " \
    #             f"from {self.TABLENAME} WHERE _is_deleted != {1} " + where_clause
    #     print (query)
    #     result_set = self.conn.execute(query).fetchall()
    #     result = [{column: row[i]
    #               for i, column in enumerate(result_set[0].keys())}
    #               for row in result_set]
    #     return result


class User:
    TABLENAME = "Users"

    def __init__(self):
        pass

    def create(self, user):
        conn = sqlite3.connect(db)
        # query = f'insert into {self.TABLENAME} ' \
        #         f'(Name, Email) ' \
        #         f'values ({name},{email})'
        data = [user['first_name'], user['last_name'], user['email']]
        data = ', '.join("'{0}'".format(w) for w in data)
        query = 'insert into ' + self.TABLENAME + '(first_name, last_name, email) ' \
                + 'values (' + data +')'
        # print(query)
        result = conn.execute(query)
        conn.commit()
        conn.close()
        return result

    def login(self, user):
        ret = 0
        conn = sqlite3.connect(db)
        conn.text_factory = str
        query = "SELECT * FROM " + self.TABLENAME + " WHERE email='" + user['email'] + "'"
        results = conn.execute(query).fetchone()
        if results:
            query = "SELECT * FROM " + self.TABLENAME + " WHERE email='" + user['email'] \
                + "' AND first_name='" + user['first_name'] + "' AND last_name='" + user['last_name'] + "'"
            conn.row_factory = sqlite3.Row
            results = conn.execute(query).fetchone()
            if not results:
                ret = 1 # name incorrect
            else:                
                results = dict(results)
        else:
            ret = 2 # email not exist, new user
        conn.commit()
        conn.close()
        return ret, results

    def get_by_id(self, user_id):
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        conn.text_factory = str
        query = "SELECT * FROM " + self.TABLENAME + " WHERE id=" + str(user_id)
        cursor = conn.execute(query)
        results = cursor.fetchone()
        results = dict(results)
        conn.commit()
        conn.close()
        return results


if __name__ == "__main__":
    pass