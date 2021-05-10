import copy

class Player():
	def __init__(self, card1, card2, qubits, number, circuit):
		self.card1 = [card1]
		self.card2 = [card2]
		self.qubits = qubits
		self.next_qubit1 = 0
		self.next_qubit2 = 0
		self.number = number
		self.circuit = circuit
		self.entangled = []
		self.next_entangle = 0
		self.current_bet = 0
		self.stack = 1000

	def get_card1(self):
		ret = ""
		for card in self.card1:
			ret = ret + str(card.name)
		return ret

	def get_card2(self):
		ret = ""
		for card in self.card2:
			ret = ret + str(card.name)
		return ret

	def get_hand_string(self):
		return "( " + self.get_card1_string + " ) " + "( "  + self.get_card2_string + " )"

	def get_card1_string(self):
		ret = ""
		for card in self.card1:
			ret = card + card.name
		return ret

	def get_card2_string(self):
		ret = ""
		for card in self.card1:
			ret = card + card.name
		return ret

	def serialize(self):
		new_player = copy.deepcopy(self)
		new_player.circuit = []
		return new_player