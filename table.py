import numpy as np
import random
import copy
import cirq
import math
from cirq import Simulator
from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator
from card import _Card
from player import Player


class Table():
	def __init__(self):
		self.flop1 = "Error"
		self.flop2 = "Error"
		self.flop3 = "Error"
		self.turn = "Error"
		self.river = "Error"
		self.cards = []
		self.deck = self.build_deck()
		player1 = Player(self.draw_card(), self.draw_card(), cirq.LineQubit.range(10), 1, cirq.Circuit())
		player2 = Player(self.draw_card(), self.draw_card(), cirq.LineQubit.range(10), 2, cirq.Circuit())
		self.all_players = [player1, player2]
		self.active_players = len(self.all_players)
		self.checked_players = 0
		self.players = self.all_players[:]
		self.current_player = 0
		# 0 - pre-flop, 1 - flop, 2 - turn, 3 - river.
		self.phase = 0
		self.finished = 0
		self.pot = 0
		self.to_pay = 0
		self.showdown = 0


	################# PLAYER ACTIONS ##################

	def check (self, player_id):
		if player_id != self.current_player:
			return "Not your turn" 
		player = self.players[self.current_player]
		response = ""
		if player.current_bet == self.to_pay:  # checa se player já cobriu aposta
			self.checked_players = self.checked_players + 1
			response = "Player " + str(self.current_player) + " has checked."
			if self.checked_players == self.active_players:  # acabou rodada de apostas
				response = response + self.next_phase()
			else:  # não acabou a rodada de apostas, passa pro proximo player
				self.next_player()
		else:
			response = "Player has not yet covered all bets."
		return response
		# else:
		# exception > players não pagou a aposta. Na real essa checagem idealmente seria feita a cada começo
		# de turno do player e desativaria o botão Check.

	def raise_bet(self, player_id, amount):
		if player_id != self.current_player:
			return "Not your turn" 
		player = self.players[self.current_player]
		total = amount + self.to_pay - player.current_bet 
		if player.stack >= total:
			self.pot = self.pot + total
			self.checked_players = 1
			self.to_pay = amount + self.to_pay 
			player.current_bet = self.to_pay
			player.stack = player.stack - total
			ret = "Player " + str(self.current_player) + " has raised to " + str(self.to_pay)
			self.next_player()
			return ret
		else:
			return "Not enough money"

	def call(self, player_id):
		if player_id != self.current_player:
			return "Not your turn" 
		if self.to_pay == 0:
			return "Nothing to call, either check or raise."
		player = self.players[self.current_player]
		response = "Player " + str(self.current_player) + " "
		total = self.to_pay - player.current_bet
		if player.stack >= total:
			self.pot = self.pot + total
			player.stack = player.stack - total
			player.current_bet = player.current_bet + self.to_pay
			self.checked_players = self.checked_players + 1
			if self.checked_players == self.active_players:  # acabou rodada de apostas
				response = response + self.next_phase()
			else:
				self.next_player()
			response = response + "has called for " + \
				str(self.to_pay) + " chips."
			return response
		else:
			response = response + "has not enough to cover, so they went all in. NOT IMPLEMENTED YET."
			return response

	def fold (self, player_id):
		del self.players[player_id]
		self.active_players = self.active_players - 1
		if self.active_players == 1:
			# acabou mão, player ganhou	
			return self.finish_hand()
		return "Player folded."

	def quantum_draw1(self, player_id):
		return self.quantum_draw(player_id, 0)


	def quantum_draw2(self, player_id):
		return self.quantum_draw(player_id, 5)

	def quantum_draw(self, player_id, offset):
		# Caso o card esteja normal, transforma em qubit
		if player_id != self.current_player:
			return "Not your turn" 
		player = self.get_active_player()
		card = "Erro no card"
		next_qubit = -1
		if offset == 0:
			card = player.card1
			next_qubit = player.next_qubit1
		elif offset == 5:
			card = player.card2
			next_qubit = player.next_qubit2

		entangle = 0

		if not entangle:
			player.circuit.append(cirq.H(player.qubits[next_qubit + offset]))

		new_cards = []
		for i in range(len(card)):
			card[i].binary_position = (self.to_bin(i, next_qubit + 1))

		i = 0

		for i in range(pow(2, next_qubit)):
			new_card = self.draw_card()
			new_card.binary_position = self.to_bin((len(card) + i), next_qubit + 1)
			new_cards.append(new_card)

		card = card + new_cards

		if offset == 0:
			player.next_qubit1 = player.next_qubit1 + 1
		else:
			player.next_qubit2 = player.next_qubit2 + 1

		if offset == 0:
			player.card1 = card
		elif offset == 5:
			player.card2 = card

		response = "Player " + str(self.current_player) + " has quantum drawed."
		return response



	################### PLAYER ACTIONS END #####################

	def serialize(self):
		new_table = copy.deepcopy(self)
		for player in self.players:
			new_player = player.serialize()
			new_table.players.append(new_player)
			new_table.all_players.append(new_player)	

		return new_table

	def finish_hand (self):
		winner = ""
		ret = ""
		if self.active_players > 1:
			self.compute_players()
			score = 0
			board = [Card(self.flop1.power, self.flop1.suit), Card(self.flop2.power, self.flop2.suit) , Card(self.flop3.power, self.flop3.suit), Card(self.turn.power, self.turn.suit), Card(self.river.power, self.river.suit)]
			for player in self.players:
				hole = [Card(player.card1[0].power, player.card1[0].suit), Card(player.card2[0].power, player.card2[0].suit)]
				new_score = HandEvaluator.evaluate_hand(hole, board)
				if new_score > score:
					score = new_score
					winner = player
					
		else:
			winner = self.players[0]
		if self.showdown == 1:
			ret = "Player " + str(player.number) + " has won " + str(self.pot) + " chips. Click on restart for another hand."
		else:
			ret = "Player " + str(self.players[0].number) + " has won."
		winner.stack = winner.stack + self.pot
		self.finished = 1
		return ret
	
	def build_deck(self):
		numbers = list(range(2, 11))
		numbers.append('J')
		numbers.append('Q')
		numbers.append('K')
		numbers.append('A')
		powers = list(range(2, 15))
		suits = ['♡', '♠', '♣', '♢']
		suits_numbers = [1, 2, 3, 4]

		deck = []
		for i in range(len(numbers))	:
			for j in range(len(suits)):
				card = _Card(str(numbers[i]) + suits[j] +
							" ", powers[i], suits_numbers[j])
				deck.append(card)

		return deck

	def next_player(self):
		self.current_player = self.current_player + 1
		if self.current_player == len(self.players):
			self.current_player = 0

	def restart_hand(self):
		if not self.finished:
			return "Hand is not over yet!"
		self.pot = 0
		self.phase = 0
		self.showdown = 0
		self.current_player = 0
		self.active_players = len(self.all_players)
		self.checked_players = 0
		self.to_pay = 0
		self.players = []
		self.deck = self.build_deck()
		for player in self.all_players:
			player.card1 = [self.draw_card()]
			player.card2 = [self.draw_card()]
		self.players = self.all_players[:]
		return "New hand!"

	def measure_players(self):
		for player in self.players:
			for i in range(player.next_qubit1):
				player.circuit.append(cirq.measure(player.qubits[i]))

			for i in range(player.next_qubit2):
				player.circuit.append(cirq.measure(player.qubits[i + 5]))

	def draw_card(self):
		position = random.randint(0, len(self.deck) - 1)
		card = self.deck.pop(position)
		return card

	def compute_players(self):
		
		self.measure_players()
		simulator = Simulator()
		for player in self.players:
			result = ''
			if player.next_qubit1 != 0 or player.next_qubit2 != 0:
				result = simulator.run(player.circuit)
			res = str(result)
			bits1 = ''
			bits2 = ''
			bit = ''
			for i in range(len(res)):
				if res[i] == '=':
					bit = bit + str(res[i + 1])

			if player.next_qubit1 > 0:
				bits1 = bit[:player.next_qubit1]
			if player.next_qubit2 > 0:
				bits2 = bit[player.next_qubit1:]

			if len(player.card1) > 1:
				player.card1 = [player.card1.pop(int(bits1, 2))]

			if len(player.card2) > 1:
				player.card2 = [player.card2.pop(int(bits2, 2))]


	def get_active_player (self):
		return self.players[self.current_player]

	def to_bin (self, x, n = 0):
		return format(x, 'b').zfill(n)

	def next_phase (self):
		self.phase = self.phase + 1
		self.checked_players = 0
		self.to_pay = 0
		self.current_player = 0

		for player in self.players:
			player.current_bet = 0

		if self.phase == 1:
			self.flop1 = self.draw_card()
			self.flop2 = self.draw_card()
			self.flop3 = self.draw_card()
			self.cards.append(self.flop1)
			self.cards.append(self.flop2)
			self.cards.append(self.flop3)

		if self.phase == 2:
			self.turn = self.draw_card()
			self.cards.append(self.turn)

		if self.phase == 3:
			self.river = self.draw_card()
			self.cards.append(self.river)


		if self.phase == 4:
			showdown = 1
			return self.finish_hand()

		return ""

