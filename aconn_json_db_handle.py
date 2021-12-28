import json


class DatabaseAconn:
    def __init__(self, db_path):
        self.db_path = db_path

    def createDB(self):
        file = open(self.db_path, "w+")
        file.write("{\"1\":\"Protector Object\"}")
        file.close()

    def appendToDB(self, dictionary):
        file_inp = open(self.db_path)
        out = json.load(file_inp)
        print(len(out))
        index = len(out) + 1
        out.update({f"{index}": dictionary})

        file = open(self.db_path, "w")

        file.write(str(out).replace("'", '"'))
        file.close()

    def getAll(self):
        return json.load(open(self.db_path))

    def filteredQuery(self, filter_dict):
        key = list(filter_dict.keys())[0]
        data = json.load(open(self.db_path))
        filtered_query = []
        for i in data:
            try:
                date_test = data[str(int(i) + 1)][f"{key}"]
                filtered_query.append(data[str(int(i) + 1)])
            except KeyError:
                pass
        return filtered_query

    def queryGet(self, index):
        file = open(self.db_path)
        out = json.load(file)
        return out[index]
