from pydantic.main import create_model
from table import Table

class Game():
    def __init__(self):
        self.table_list = []
        self.table_top = None

    def create_table (self, num_players, user):
        new_table = Table(num_players)
        user.player = new_table.all_players[0]
        self.table_list.append(new_table)
        self.table_top = new_table
        return new_table

    def get_list(self):
        return self.table_list
    
    def find_table (self, user):
        if self.table_top:    
            player = self.table_top.add_player()
            user.player = player
            ret = self.table_top
            self.table_top = None
            return ret
        else:
            return self.create_table(1, user)        

    