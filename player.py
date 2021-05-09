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

	def to_JSON(self):
		return self