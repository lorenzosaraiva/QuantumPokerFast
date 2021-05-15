import copy

class Player():
	def __init__(self, card1, card2, qubits, number, circuit):
		self.card1 = [card1]
		self.card2 = [card2]
		self.card1_active = [card1]
		self.card2_active = [card2]
		self.qubits = qubits
		self.next_qubit1 = 0
		self.next_qubit2 = 0
		self.number = number
		self.circuit = circuit
		self.entangled1 = []
		self.entangled2 = []
		self.diff_ent = 0
		self.diff_ent_index = []
		self.next_entangle = 0
		self.current_bet = 0
		self.stack = 1000

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
		self.next_entangle = 0
		self.current_bet = 0

	def serialize(self):
		new_player = copy.deepcopy(self)
		new_player.circuit = []
		new_player.qubits = []
		return new_player