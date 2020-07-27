class SudokuPuzzle:

	def __init__(self):
		self.side_length = 9
		self.sub_side_length = 3
		self._grid = []
		self.__clear_grid()
		# number set should never contain any false equivalent values or this program will fail
		self.number_set = set(range(1, 10))

	def get_row(self, row):
		return tuple(self._grid[row])

	def get_column(self, column):
		return tuple(x[column] for x in self._grid)

	def get_subgrid(self, row, column):
		"""
		Returns the subgrid of the given row and column.

		:param row: The inside the subgrid.
		:param column: The column inside the subgrid.
		:return: A tuple representing the subgrid that the given row/column is in.
		"""
		# need to check that the subside length definitely divides the side length equally
		# (its okay for now doing "classic" sudoku puzzles)
		row_offset = (row // self.sub_side_length) * self.sub_side_length
		column_offset = (column // self.sub_side_length) * self.sub_side_length
		if row_offset >= self.side_length or column_offset >= self.side_length:
			raise ValueError(
				f"{row}, {column} is not a valid subgrid position in a puzzle with side length {self.side_length} and sub side length {self.sub_side_length}")
		subgrid = [0] * (self.side_length // self.sub_side_length)
		for i in range(len(subgrid)):
			subgrid[i] = self.get_row(row_offset + i)[column_offset:column_offset + self.sub_side_length]
		return tuple(subgrid)

	def get_tile(self, row, column):
		if row >= self.side_length or column >= self.side_length:
			raise ValueError(f"{row}, {column} is not a valid position in a puzzle with side length {self.side_length}")
		return self._grid[row][column]

	def __set_tile(self, row, column, value):
		if value not in self.number_set:
			raise ValueError(
				f"{value} is not a valid value in this puzzle. Valid values are: {', '.join(str(x) for x in self.number_set)}")
		if row >= self.side_length or column >= self.side_length:
			raise ValueError(f"{row}, {column} is not a valid position in a puzzle with side length {self.side_length}")
		self._grid[row][column] = value

	def __set_subgrid_tile(self, sub_row, sub_col, row, column, value):
		"""
		Sets the value of a tile within a given subgrid.

		:param sub_row: The subgrid row.
		:param sub_col: The subgrid column.
		:param row: The row in the subgrid.
		:param column: The column in the subgrid.
		:return: None
		"""
		row_offset = row * self.sub_side_length
		column_offset = column * self.sub_side_length
		if row_offset >= self.side_length or column_offset >= self.side_length:
			raise ValueError(
				f"{row}, {column} is not a valid subgrid position in a puzzle with side length {self.side_length} and sub side length {self.sub_side_length}")
		if sub_row >= self.sub_side_length or sub_col >= self.sub_side_length:
			raise ValueError(
				f"{sub_row}, {sub_col} is not a valid position in a subgrid with side length {self.sub_side_length}")
		self.__set_tile(row_offset + row, column_offset + column, value)

	def is_full(self):
		"""
		Checks if the puzzle is populated with values in its number set.

		:return: True if the puzzle only contains values from its number set. False otherwise.
		"""
		full = True
		for i in range(self.side_length):
			for j in range(self.side_length):
				full = full and self.get_tile(i, j) in self.number_set
		return full

	def is_valid(self):
		"""
		Checks that no value is repeated in a row, column or subgrid (i.e. the 3x3 tiles in a 9x9 grid).

		:return: True if every value in evey row/column is unique in that row. False otherwise
		"""
		valid = self.contains_invalid_values()
		for i in range(self.side_length):
			# might need to double check that side length and length of number set is the same
			# * (puzzle is impossible if number set is shorter)
			# * (puzzle is wrong if number set is longer)
			valid = valid and len(set(self.get_row(i))) == self.side_length
			valid = valid and len(set(self.get_column(i))) == self.side_length

		return valid

	def is_complete(self):
		return self.is_full() and self.is_valid()

	def contains_invalid_values(self):
		"""
		Checks that the puzzle doesn't contain values that is shouldn't.
		These values are anything not in the puzzles number set or 0.

		:return: True if the puzzle contains values it shouldn't. False otherwise.
		"""
		invalid = False
		for i in range(self.side_length):
			invalid = invalid or any([x not in self.number_set and x != 0 for x in self.get_row(i)])
			# Could remove the above or below line (but not both) without affecting this method
			invalid = invalid or any([x not in self.number_set and x != 0 for x in self.get_column(i)])
		return invalid

	def __generate_puzzle(self):
		"""
		Generates a solvable sudoku puzzle. If a puzzle already exists it will be overwritten.

		:return: None
		"""
		self.__clear_grid()

	def __clear_grid(self):
		"""
		Clears the puzzle grid. This can be done in order to prepare for a new puzzle to be made.

		:return: None
		"""
		# a clear grid should always consist of false equivalent values in order for this program to work
		self._grid = [[0 for i in range(self.side_length)] for j in range(self.side_length)]

	def solve(self):
		if not self.is_valid():
			raise Exception("The puzzle that is trying to be solved is invalid and will not have a solution.")
		change_made = False
		# TO SOLVE LOGICALLY
		# 1. Fill in obvious tiles
		# 2. If solved: Return
		# 3. Mark remaining tiles with set of all possible values
		# 4. Fill in tiles with singleton sets
		# 5. If not solved return to step 1.

		# 1.
		for r in range(0, self.side_length, self.sub_side_length):
			for c in range(0, self.side_length, self.sub_side_length):
				unplaced_number_set = self.number_set.difference(set([x for y in self.get_subgrid(r, c) for x in y]))
				if len(unplaced_number_set) > 0:
					for n in unplaced_number_set:
						valid_places = set(
							[(x, y) for x in range(self.sub_side_length) for y in range(self.sub_side_length) if
							 not self.get_tile(x + r, y + c)])
						# here we have:
						# * (c,r) are the coordinates of a subgrid.
						# * c = subgrid column no.
						# * r = subgrid row no.
						# * valid_places is (r,c) of empty tiles in the subgrid
						# * n = a value from the number set
						# * n is not already in the subgrid
						for i in range(self.sub_side_length):
							if n in self.get_row(r + i):
								valid_places = valid_places.difference(set([i, x] for x in range(self.sub_side_length)))
							if n in self.get_column(c + i):
								valid_places = valid_places.difference(set([x, i] for x in range(self.sub_side_length)))
						if len(valid_places) == 0:
							raise Exception(
								f"Unable to place {n} in the puzzle in subgrid with top left tile row: {r} column: {c}.")
						elif len(valid_places) == 1:
							self.__set_tile(r + valid_places[0][0], c + valid_places[0][1], n)
							change_made = True
		# 2.
		if self.is_complete():
			print("PUZZLE SOLVED")
			return self
		# 3. todo
		if not change_made:
			raise Exception("The solving algorithm has insufficient ability to solve this puzzle.")
		else:
			self.solve()
