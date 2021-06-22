from pydantic.main import create_model
from table import Table

class Game():
    def __init__(self):
        self.table_list = []
        self.table_top = None

    def create_table (self, user):
        new_table = Table()
        new_table.add_player(user)
        self.table_list.append(new_table)
        self.table_top = new_table
        return new_table

    def get_list(self):
        return self.table_list
    
    def find_or_create_table (self, user):
        if self.table_top:    
            self.table_top.add_player(user)
            ret = self.table_top
            self.table_top = None
            return ret
        else:
            return self.create_table(user) 

    def get_player (self, username):
        for table in self.table_list:
            player = table.get_player(username)
            if player:
                return player.serialize()
        return None

    def get_table (self, username):
        for table in self.table_list:
            player = table.get_player(username)
            if player:
                return table
        return None
