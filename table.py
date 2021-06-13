import numpy as np
import random
import copy
import cirq
import math
import time

from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator
from card import _Card
from player import Player


class Table():
	def __init__(self, num_players):
		self.flop1 = "Error"
		self.flop2 = "Error"
		self.flop3 = "Error"
		self.turn = "Error"
		self.river = "Error"
		self.cards = []
		self.deck = self.build_deck()
		self.all_players = []
		self.max_qubits = 5
		for i in range(num_players):
			player = Player(self.draw_card(), self.draw_card(), cirq.LineQubit.range(self.max_qubits * 2), i, cirq.Circuit())		
			player.table = self
			self.all_players.append(player)
		self.active_players = len(self.all_players)
		self.checked_players = 0
		# 0 - pre-flop, 1 - flop, 2 - turn, 3 - river.
		self.phase = 0
		self.finished = 0
		self.pot = 0
		self.to_pay = 0
		self.showdown = 0
		self.quantum_pot = 0
		self.small_blind = 10
		self.big_blind = 20 
		self.quantum_draw_price = 3 * self.big_blind
		self.dealer = 0
		self.players_allin = 0
		self.current_player = self.get_next_player_index(self.dealer)
		self.players_to_call = []
		for i in range(num_players):
			self.players_to_call.append(0)
		self.set_blinds()
		self.side_pots = []
		self.showdown_players = []
		


	################# PLAYER ACTIONS ##################

	def check (self, player_id):
		basic_checks = self.basic_checks(player_id)
		if basic_checks != 1:
			return basic_checks
		player = self.all_players[self.current_player]
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

	def raise_bet (self, player_id, amount=100):
		basic_checks = self.basic_checks(player_id)
		if basic_checks != 1:
			return basic_checks

		if amount <= 0: 
			return "Invalid value" 
		if self.active_players == 1:
			return "Can only call or fold"

		player = self.all_players[self.current_player]
		total = amount + self.to_pay - player.current_bet 
		if player.stack >= total:
			self.pot = self.pot + total
			self.checked_players = 1
			self.to_pay = amount + self.to_pay 
			player.current_bet = self.to_pay
			player.stack = player.stack - total
			ret = "Player " + str(self.current_player) + " has raised to " + str(self.to_pay)

			i = 0
			for call_player in self.all_players:
				if call_player.is_folded == 1 or call_player.is_allin == 1:
					self.players_to_call[i] = 0
				else:
					self.players_to_call[i] = self.to_pay - call_player.current_bet
				i += 1

			if player.stack == 0:
				self.active_players = self.active_players - 1
				self.players_allin = self.players_allin + 1
				self.checked_players = 0
				player.is_allin = 1

			self.next_player()	
			return ret
		else:
			return "Not enough money"

	def call (self, player_id):
		basic_checks = self.basic_checks(player_id)
		if basic_checks != 1:
			return basic_checks 
		if self.to_pay == 0:
			return "Nothing to call, either check or raise."
		player = self.all_players[self.current_player]
		response = "Player " + str(self.current_player) + " "
		total = self.to_pay - player.current_bet
		if player.stack > total:
			self.pot = self.pot + total
			player.stack = player.stack - total
			player.current_bet = self.to_pay
			self.checked_players = self.checked_players + 1
			self.players_to_call[self.current_player] = 0
			if self.active_players == 1:
				self.resolve_all_in()
			elif self.checked_players == self.active_players:  # acabou rodada de apostas
				response = response + self.next_phase()
			else:
				self.next_player()
			response = response + "has called for " + \
				str(self.to_pay) + " chips."
		else:
			player.is_allin = 1
			self.pot = self.pot + player.stack
			player.current_bet = player.stack + player.current_bet
			player.stack = 0
			self.active_players = self.active_players - 1
			self.players_allin = self.players_allin + 1
			if self.active_players == 1:
				self.resolve_all_in()
			elif self.checked_players == self.active_players and self.active_players > 1: 
				response = response + self.next_phase()
			else:
				self.next_player()
			response = response + "You had not enough chips to cover the bet, so you went all in."
		return response

	def fold (self, player_id):
		basic_checks = self.basic_checks(player_id)
		if basic_checks != 1:
			return basic_checks
		player = self.all_players[player_id]
		player.is_folded = 1
		self.active_players = self.active_players - 1
		if self.active_players <= 1:
			if self.players_allin <= 1:
				return self.finish_hand()
			else:
				return self.resolve_all_in()
		else:
			if self.checked_players == self.active_players:  # acabou rodada de apostas
				self.next_phase()
			else:
				self.next_player()

	def quantum_draw1 (self, player_id):
		return self.quantum_draw(player_id, 0, False)

	def quantum_draw2 (self, player_id):
		return self.quantum_draw(player_id, self.max_qubits, False)

	def quantum_draw (self, player_id, offset, entangle):
		# Caso o card esteja normal, transforma em qubit
		basic_checks = self.basic_checks(player_id)
		if basic_checks != 1:
			return basic_checks

		if self.quantum_action_used == 1:
			return "Quantum Action already used this turn."

		player = self.get_active_player()

		if player.stack < self.quantum_draw_price:
			return "Not enough chips to pay Quantum Draw price."
		else:
			self.pot = self.pot + self.quantum_draw_price
			self.quantum_pot = self.quantum_pot + self.quantum_draw_price
			player.stack = player.stack - self.quantum_draw_price	
		#card = "Erro no card"
		#next_qubit = -1
		if offset == 0:
			card = player.card1
			next_qubit = player.next_qubit1
		else:
			card = player.card2
			next_qubit = player.next_qubit2
		
		if next_qubit >= self.max_qubits:
			return "All qubits already used"

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
		else:
			player.card2 = card

		self.update_player_post_entangle(player)
		response = "Player " + str(self.current_player) + " has quantum drawed."
		return response

	def entangle_same_card1 (self, player_id):
		if self.finished == 1:
			return "Hand is over. Click on restart for another hand."
		if self.quantum_action_used == 1:
			return "Quantum Action already used this turn."
		return self.entangle_same_card(player_id, 0)

	def entangle_same_card2 (self, player_id):
		if self.finished == 1:
			return "Hand is over. Click on restart for another hand."
		if self.quantum_action_used == 1:
			return "Quantum Action already used this turn."
		return self.entangle_same_card(player_id, self.max_qubits)


	def entangle_same_card (self, player_id, offset):
		if player_id != self.current_player:
			return "Not your turn"
		player = self.all_players[self.current_player]
		ret = ""
		if offset == 0:
			next_qubit = player.next_qubit1
		else:
			next_qubit = player.next_qubit2

		if next_qubit == 0: # Tentou fazer o entangle de um card sem qubit ativado
			ret = "You don't have any active qubits in this card! Quantum draw first."
			return ret

		if next_qubit >= 5:
			ret = "All qubits already used."
			return ret
		
		origin = next_qubit - 1
		player.circuit.append(cirq.CNOT(player.qubits[origin  + offset], player.qubits[next_qubit + offset]))
		self.quantum_draw(player_id, offset, True)

		#player.entangled.append(['c'+ str('1') + 'q' + str(origin), 'c' + str('1') + 'q' + str(next_qubit)])
		if offset == 0:
			player.entangled1.append([origin, next_qubit])
		else:
			player.entangled2.append([origin, next_qubit])

		self.update_player_post_entangle(player)
		ret = "Player " + str(self.current_player) + " has entangled."
		return ret
	
	def entangle_diff_1_2 (self, player_id):
		if self.finished == 1:
			return "Hand is over. Click on restart for another hand."
		if self.quantum_action_used == 1:
			return "Quantum Action already used this turn."
		if player_id != self.current_player:
			return "Not your turn"
		player = self.all_players[self.current_player]
		
		origin = player.next_qubit1 - 1
		target = player.next_qubit2

		if origin < 0: # Tentou fazer o entangle de um card sem qubit ativado
			ret = "You don't have any active qubits in the origin card! Quantum draw first."
			return ret

		if target >= 5:
			ret = "All qubits already used."
			return ret

		player.diff_ent_index.append([origin, target])
		player.circuit.append(cirq.CNOT(player.qubits[origin], player.qubits[target + 5]))
		self.quantum_draw(player_id, 5, True)

		player.diff_ent = 1
		self.update_player_post_entangle(player)
		ret = "Player " + str(self.current_player) + " has entangled."
		return ret

	def entangle_diff_2_1 (self, player_id):
		if self.finished == 1:
			return "Hand is over. Click on restart for another hand."
		if self.quantum_action_used == 1:
			return "Quantum Action already used this turn."
		if player_id != self.current_player:
			return "Not your turn"
		player = self.all_players[self.current_player]

		
		origin = player.next_qubit2 - 1
		target = player.next_qubit1

		if origin < 0: # Tentou fazer o entangle de um card sem qubit ativado
			ret = "You don't have any active qubits in the origin card! Quantum draw first."
			return ret

		if target >= 5:
			ret = "All qubits already used."
			return ret

		player.circuit.append(cirq.CNOT(player.qubits[origin + self.max_qubits], player.qubits[target]))
		self.quantum_draw(player_id, 0, True)

		player.diff_ent = 1
		player.diff_ent_index.append([target, origin])
		self.update_player_post_entangle(player)
		ret = "Player " + str(self.current_player) + " has entangled."
		return ret

	################### PLAYER ACTIONS END #####################

	def basic_checks(self, player_id):
		if len(self.all_players) == 1:
			return "Please wait for another player"
		if player_id != self.current_player:
			return "Not your turn"
		if self.finished:
			return "Hand is over. Click on restart for another hand."
		return 1


	def serialize (self):
		new_table = copy.deepcopy(self)
		new_table.all_players = []
		new_table.showdown_players = []
		for player in self.all_players:
			new_player = player.serialize()
			new_table.all_players.append(new_player)	
		
		for player in self.showdown_players:
			new_player = player.serialize()
			new_table.showdown_players.append(new_player)	

		return new_table
	
	def add_player (self):
		current_players = len(self.all_players)
		qubits = cirq.LineQubit.range(self.max_qubits * 2)
		new_player = Player(self.draw_card(), self.draw_card(), qubits, current_players, cirq.Circuit())
		new_player.table = self
		self.all_players.append(new_player)
		self.players_to_call.append(0)
		self.finished = 1
		self.restart_hand()
		return new_player

	def update_player_post_entangle (self, player):
		#self.quantum_action_used = 1

		to_remove = []
		for i in range(len(player.card1)):
			binary = self.to_bin(i, player.next_qubit1)
			for pair in player.entangled1:
				if binary[pair[0]] != binary[pair[1]]:
					to_remove.append(i)


		to_remove = list(dict.fromkeys(to_remove))
		temp_list = player.card1[:]
		for index in sorted(to_remove, reverse=True):
			del temp_list[index]

		player.card1_active = temp_list

		
		to_remove = []
		for i in range(len(player.card2)):
			binary = self.to_bin(i, player.next_qubit2)
			for pair in player.entangled2:
				if binary[pair[0]] != binary[pair[1]]:
					to_remove.append(i)


		to_remove = list(dict.fromkeys(to_remove))
		temp_list = player.card2[:]
		for index in sorted(to_remove, reverse=True):
			del temp_list[index]
		
		player.card2_active = temp_list

		hand1 = [[],[]]
		hand2 = [[],[]]
		if player.diff_ent == 1:
			for i in range(len(player.card1_active)):
				binary = player.card1_active[i].binary_position
				for pair in player.diff_ent_index:
					if binary[pair[0]] == '0':
						hand1[0].append(player.card1_active[i])
					else:
						hand2[0].append(player.card1_active[i])

			for i in range(len(player.card2_active)):
				binary = player.card2_active[i].binary_position
				for pair in player.diff_ent_index:
					if binary[pair[1]] == '0':
						hand1[1].append(player.card2_active[i])
					else:
						hand2[1].append(player.card2_active[i])

			player.card1_active = hand1
			player.card2_active = hand2	


	def get_call_amount (self, player_id):
		ret = self.to_pay - self.all_players[player_id].current_bet
		return ret
	
	def top_up (self, player_id):
		self.all_players[player_id].stack += 1000
		return "Player got another 1000 chips"

	def set_blinds (self):
		small = self.get_next_player_index(self.dealer)
		big = self.get_next_player_index(small)
		self.raise_bet(small, self.small_blind)
		self.raise_bet(big, self.small_blind)
		self.checked_players = 0

	def finish_hand (self):
		if self.active_players + self.players_allin <= 1:
			for player in self.all_players:
				if player.is_folded == 0:
					winner = player
					winner.stack = winner.stack + self.pot
					self.finished = 1
					return "Player " + str(winner.number) + " won " + str(self.pot) + "chips. Click on restart for another hand."				
		else:
			self.compute_players()
			board = [Card(self.flop1.power, self.flop1.suit), Card(self.flop2.power, self.flop2.suit) , Card(self.flop3.power, self.flop3.suit), Card(self.turn.power, self.turn.suit), Card(self.river.power, self.river.suit)]
			for player in self.all_players:
				if player.is_folded == 0:
					self.showdown_players.append(player)

			############# 2 PLAYERS ONLY ############
			if len(self.all_players) == 2:
				player0 = self.all_players[0]
				player1 = self.all_players[1]
				hand0 = [Card(player0.card1[0].power, player0.card1[0].suit), Card(player0.card2[0].power, player0.card2[0].suit)]
				hand1 = [Card(player1.card1[0].power, player1.card1[0].suit), Card(player1.card2[0].power, player1.card2[0].suit)]
				score0 = HandEvaluator.evaluate_hand(hand0, board)
				score1 = HandEvaluator.evaluate_hand(hand1, board)
				
				if score0 != score1:
					if score0 > score1:
						winner = player0
						loser = player1
					else:
						winner = player1
						loser = player0
					before_stack = winner.stack
					winner.stack = winner.stack + winner.total_bet 
					winner.stack = winner.stack + self.quantum_pot 

					if winner.total_bet > loser.total_bet:
						winner.stack = winner.stack + loser.total_bet
					else:
						winner.stack = winner.stack + winner.total_bet
						loser.stack = loser.stack + loser.total_bet - winner.total_bet
					chips_won = winner.stack - before_stack
					ret = "Player " + str(self.current_player) + " won " + str(chips_won) + " chips."
				else:
					player0.stack = player0.stack + player0.total_bet + (self.quantum_pot/2)
					player1.stack = player1.stack + player1.total_bet + (self.quantum_pot/2)
					ret = "Hand was a tie. Pot split." 


				self.finished = 1
				return ret + "Click on restart for another hand."

			################ 2 PLAYERS ONLY END #################

			paylist = self.all_players[:]
			chips_paid = 0 

			while chips_paid <= self.pot and len(paylist) > 0:
				score = 0
				winners = []
				for player in self.showdown_players:
					if player.is_folded:
						new_score = -1
					else:
						hole = [Card(player.card1[0].power, player.card1[0].suit), Card(player.card2[0].power, player.card2[0].suit)]
						new_score = HandEvaluator.evaluate_hand(hole, board)
					if new_score >= score:
						if new_score == score:
						  	winners.append(player)
						else:
						 	winners = [player]
					score = new_score


				current_pay = 0
				to_remove = []
								
				for winner in winners:
					winner_bet = winner.total_bet

					# vencedor será removido da paylist
					to_remove.append(winner)

					# vencedor ganha de volta o que apostou na mão
					chips_paid = chips_paid + winner_bet
					winner.stack = winner.stack + winner_bet
					current_pay = current_pay + winner_bet	

					# percorre os jogadores que ainda tem que pagar
					for player in paylist:
						# pula o próprio vencedor
						if player.number != winner.number:
							# caso a aposta do player atual seja menor que do vencedor
							if player.total_bet > winner_bet:
								# tira do player atual um valor igual a aposta do vencedor							
								winner.stack = winner.stack + winner_bet
								chips_paid = chips_paid + winner_bet
								current_pay = current_pay + winner_bet		
								player.total_bet = player.total_bet - winner_bet
							else:
								winner.stack = winner.stack + player.total_bet
								chips_paid = chips_paid + player.total_bet
								current_pay = current_pay + player.total_bet		
								player.total_bet = 0
								to_remove.append(player)

				# Remove os vencedores que já cobraram e os que não tem nada mais a pagar.
				for player in to_remove:
					self.showdown_players.remove(player)
				ret = ret + "Player " + str(winner.number) + " has won " + str(current_pay) + " chips."
		
				

		ret = ret + " Click on restart for another hand."
		self.finished = 1
		return ret
	
	def build_deck (self):
		numbers = list(range(2, 11))
		numbers.append('J')
		numbers.append('Q')
		numbers.append('K')
		numbers.append('A')
		powers = list(range(2, 15))
		suits = ['H', 'S', 'C', 'D']
		suits_numbers = [1, 2, 3, 4]

		deck = []
		for i in range(len(numbers)):
			for j in range(len(suits)):
				card = _Card(str(numbers[i]) + suits[j], powers[i], suits_numbers[j])
				deck.append(card)

		return deck

	def next_player (self):
		#print("called next player ")
		no_actives = 1
		for player in self.all_players:
			if player.is_allin == 0 and player.is_folded == 0:
				no_actives = 0
		if no_actives:
			self.resolve_all_in()
		else:
			self.quantum_action_used = 0
			while True:
				self.current_player = self.current_player + 1
				if self.current_player == len(self.all_players):
					self.current_player = 0
				player = self.all_players[self.current_player]
				if player.is_allin == 0 and player.is_folded == 0:
					break
				
		
	def resolve_all_in (self):
		while self.phase != 4:
			self.next_phase()




	def get_next_player_index (self, index):
		if index == len(self.all_players) - 1:
			return 0
		return index + 1

	def restart_hand (self):

		if not self.finished:
			return "Hand is not over yet!"
		if self.all_players[0].stack == 0 or self.all_players[1].stack == 0:
			return "Only one player. Top up before playing another hand"
		self.pot = 0
		self.phase = 0
		self.showdown = 0
		self.finished = 0
		self.quantum_pot = 0
		self.active_players = len(self.all_players)
		self.checked_players = 0
		self.players_allin = 0
		self.to_pay = 0
		self.cards = []
		self.deck = self.build_deck()
		for player in self.all_players:
			player.reset_player(self.draw_card(), self.draw_card(), cirq.LineQubit.range(self.max_qubits * 2), cirq.Circuit())
		self.dealer = self.get_next_player_index(self.dealer)
		self.current_player = self.get_next_player_index(self.dealer)
		self.quantum_action_used = 0 
		self.set_blinds()
		self.showdown_players = []
		return "New hand!"

	def measure_players (self):
		for player in self.all_players:
			if player.is_folded == 1:
				continue
			for i in range(player.next_qubit1):
				player.circuit.append(cirq.measure(player.qubits[i]))

			for i in range(player.next_qubit2):
				player.circuit.append(cirq.measure(player.qubits[i + self.max_qubits]))

	def draw_card (self):
		position = random.randint(0, len(self.deck) - 1)
		card = self.deck.pop(position)
		return card

	def compute_players (self):
		
		self.measure_players()
		simulator = cirq.Simulator()
		for player in self.all_players:
			if player.is_folded == 1:
				continue
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
		return self.all_players[self.current_player]

	def to_bin (self, x, n = 0):
		return format(x, 'b').zfill(n)

	def next_phase (self):
		self.phase = self.phase + 1
		self.to_pay = 0
		self.checked_players = 0
		self.current_player = self.dealer
		first_player = self.all_players[self.dealer]
		if (first_player.is_allin == 1 or first_player.is_folded == 1) and self.active_players > 1:
			self.next_player()

		self.quantum_action_used = 0

		for player in self.all_players:
			player.total_bet = player.total_bet + player.current_bet
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
			self.showdown = 1
			return self.finish_hand()

		return ""

