import copy

class MP(type):
	def __repr__(self):
		return self.user.username

class Player():
	
	__metaclass__ = MP

	def __init__(self, card1, card2, qubits, number, circuit, username, table):
		self.card1 = [card1]
		self.card2 = [card2]
		self.card1_active = [card1]
		self.card2_active = [card2]
		self.qubits = qubits
		self.next_qubit1 = 0
		self.next_qubit2 = 0
		self.id = number
		self.circuit = circuit
		self.entangled1 = []
		self.entangled2 = []
		self.diff_ent = 0
		self.diff_ent_index = []
		self.next_entangle = 0
		self.current_bet = 0
		self.total_bet = 0
		self.to_call = 0
		self.is_allin = 0
		self.stack = 10000
		self.is_folded = 0
		self.showdown = 0
		self.table = None 
		self.username = username	

	def reset_player(self, card1, card2, qubits, circuit):
		self.card1 = [card1]
		self.card2 = [card2]
		self.card1_active = [card1]
		self.card2_active = [card2]
		self.qubits = qubits
		self.next_qubit1 = 0
		self.next_qubit2 = 0
		self.circuit = circuit
		self.entangled1 = []
		self.entangled2 = []
		self.diff_ent = 0
		self.diff_ent_index = []
		self.next_entangle = 0
		self.current_bet = 0
		self.total_bet = 0
		self.is_allin = 0
		if self.stack == 0:
			self.is_folded = 1
		else:
			self.is_folded = 0


	def serialize(self):
		new_player = copy.deepcopy(self)
		new_player.circuit = []
		new_player.qubits = []
		return new_player

	################################ ACTIONS ##################################

	def check (self):
		return self.table.check(self.id)

	def raise_bet (self, amount=100):
		return self.table.raise_bet(self.id, amount)
		
	def call (self):
		return self.table.call(self.id)

	def fold (self):
		return self.table.fold(self.id)
