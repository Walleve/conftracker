from models import Record
from models import User as UserModel
from datetime import datetime
from flask_login import UserMixin

def str2date(date):
    return datetime.strptime(date, '%Y-%m-%d')

class RecordService:
    def __init__(self):
        self.model = Record()

    def add(self, item):
        return self.model.create(item)

    def edit(self, item):
        return self.model.update(item)

    def update(self, item_id, params):
        return self.model.update(item_id, params)

    def delete(self, item_id):
        return self.model.delete(item_id)

    def list(self, user_id=0, category='all', sort='subdate', star=0):
        query_args = "(enddate='' OR enddate >= date('now'))"
        if user_id > 0 and star == 1:
            query_args += "AND subscribers LIKE '%," + str(user_id) + ",%' "
        if category != "all":
            # TODO: To handle multiple categories
            query_args += "AND category LIKE '%" + category + "'"
        data = self.model.get_items(query_args, sort)
        countries = set()
        for i, item in enumerate(data):
            if item['startdate'] != '' and '0000' not in item['startdate']:
                dates = str2date(item['startdate']).strftime('%b %d') + " - " + str2date(item['enddate']).strftime('%b %d, %Y') 
            else:
                dates = "TBD"
            data[i]['dates'] = dates
            if data[i]['category']:
                data[i]['category'] = data[i]['category'].split(",")
            else:
                data[i]['category'] = ""
            if item['subscribers'] and (',' + str(user_id) + ',' in item['subscribers']):
                data[i]['star'] = 1
            else:
                data[i]['star'] = 0
            # data[i]['subdate'] = str2date(item['subdate']).strftime('%a %b %d, %Y') 
            # data[i]['absdate'] = str2date(item['absdate']).strftime('%a %b %d, %Y') 
            # data[i]['notifdate'] = str2date(item['notifdate']).strftime('%a %b %d, %Y') 
            # data[i]['crdate'] = str2date(item['crdate']).strftime('%a %b %d, %Y') 
            countries.add(item['country'])
        # fields = [col[0] for col in desc]
        # data = [dict(zip(fields, row))  
        #     for row in results]
        return data, countries

    def subscribe(self, conf, user):
        return self.model.subscribe(conf, user)

    def get_item(self, conf_id):
        return self.model.get_item(conf_id)


class User(UserMixin):
    def __init__(self, id, first_name, last_name, email):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def is_active(self):
        return self.is_active()
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def get_id(self):
        return self.id

class UserService:
    def __init__(self):
        self.model = UserModel()

    def add(self, user):
        ret = self.model.create(user)
        # user_obj = User(user['id'], user['first_name'], user['last_name'], user['email'])
        return self.login(user)

    def login(self, user):
        status, user = self.model.login(user)
        user_obj = None
        if status == 0:
            user_obj = User(user['id'], user['first_name'], user['last_name'], user['email'])
        return status, user_obj

    def get_by_id(self, user_id):
        user = self.model.get_by_id(user_id)
        user_obj = None
        if user:
            print(user)
            user_obj = User(user['id'], user['first_name'], user['last_name'], user['email'])
        return user_obj



