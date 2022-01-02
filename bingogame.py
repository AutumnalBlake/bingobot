import random

class BingoGame:
	def __init__(self, player1, player2, channel, size = 5, freespace = True):
		if size not in (3, 5, 7):
			raise ValueError("Size must be 3, 5 or 7")

		self.players = (player1, player2)
		self.channel = channel
		self.size = size

		self.drawn = ["FS"]
		
		# Numbers are chosen from 1 to twice the grid size
		# e.g. for a 5x5 grid, numbers are chosen from 1 to 50
		self.numChoices = list(range(1, ((size ** 2) * 2) + 1))

		random.shuffle(self.numChoices)
		board1 = self.numChoices[:size ** 2]
		random.shuffle(self.numChoices)
		board2 = self.numChoices[:size ** 2]

		self.boards = (board1, board2)

		if freespace:
			for b in self.boards:
				b[size ** 2 // 2] = "FS"

	def __str__(self):
		width = self.size * 3 - 1
		s = f"{self.players[0].center(width)[:width]}     {self.players[1].center(width)[:width]}\n"
		s += "-" * width + "     " + "-" * width + "\n"
		for i in range(self.size):
			s += " ".join(str(n).ljust(2) for n in self.boards[0][i * self.size : (i + 1) * self.size])
			s += "     "
			s += " ".join(str(n).ljust(2) for n in self.boards[1][i * self.size : (i + 1) * self.size])
			s += "\n"
		return s

	# Draw a number, and return it
	def draw(self):
		num = random.choice(self.numChoices)
		self.drawn.append(num)
		self.numChoices.remove(num)
		return num

	def hasBingo(self, player):
		if player not in (0, 1):
			raise ValueError("Player must be an index 0 or 1")
		
		for i in range(self.size):
			# Check rows
			if all(n in self.drawn for n in self.boards[player][i * self.size : (i + 1) * self.size]):
				return True

			# Check cols
			if all(n in self.drawn for n in self.boards[player][i::self.size]):
				return True

		# Check \ diagonal (multiples of size + 1)
		if all(n in self.drawn for n in self.boards[player][::self.size + 1]):
			return True
		
		# Check / diagonal (multiples of size - 1 except 0)
		if all(n in self.drawn for n in self.boards[player][self.size - 1::self.size - 1]):
			return True

		return False


b = BingoGame("autumnalblake", "asjhdfkagsjdaksjdf", 3, 5, True)
print(b)
while not b.hasBingo(0) and not b.hasBingo(1):
	print(b.draw())