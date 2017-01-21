from pymongo import MongoClient
# db.links.update({}, {"$set": {'processed': false}}, {'multi':true}, false)


class DB():

    def __init__(self):
        self.host = "localhost"
        self.port = 27017
        self.db_name = "sijanscrap"
        self.conn = MongoClient(self.host, self.port)
        self.db = self.conn[self.db_name]
        # self.db.authenticate(self.username, self.password)

    def add_links(self, link):
        self.db['links'].insert(link)

    def get_one_unprocessed(self):
        result = self.db['links'].find_one({'processed': False})
        if result:
            return result
        else:
            return None

    def update_link(self, link):
        self.db["links"].update(
            {"link": link},
            {"$set": {'processed': True}},
            upsert=False,
            multi=True
        )

    def add_data(self, data):
        self.db["data"].update(data, data, upsert=True)

    def get_all(self):
        return self.db['data'].find()
