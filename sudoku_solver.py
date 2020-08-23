import json
import copy
import math as maths  # because god save the queen


class SudokuPuzzle:

	def __init__(self):
		self.side_length = 9
		self.sub_side_length = 3
		self.difficulty = None  # todo
		self._grid = []
		self.__clear_grid()
		self._solved_grid = copy.deepcopy(self._grid)
		# number set should never contain any false equivalent values or this program will fail
		self.number_set = set(range(1, 10))

	def __set_grid(self, grid):
		"""
		Sets the grid object of the puzzle.
		When the grid is changed, the other class variables are also changed.

		:param grid: The new grid object to apply.
		:return: None
		"""
		print(f"SETTING GRID...", end=" ", flush=True)
		if not isinstance(grid, list):
			print(f"FAILED - SEE EXCEPTION")
			raise TypeError(f"Expected grid to be of type list, actual type: {type(grid)}")
		if any([len(x) != len(grid) for x in grid]):
			print(f"FAILED - SEE EXCEPTION")
			raise TypeError(f"Expected grid length to be equivalent to width.")
		if len(grid) < 4:
			print(f"FAILED - SEE EXCEPTION")
			raise TypeError(
				f"Grid with side length {len(grid)} is too small to be a valid puzzle. Minimum length is 4x4.")
		# method for calculating whether the side length is a perfect square adapted from:
		# https://djangocentral.com/python-program-to-check-if-a-number-is-perfect-square/
		if not int(maths.sqrt(len(grid)) + 0.5) ** 2 == len(grid):
			print(f"FAILED - SEE EXCEPTION")
			raise TypeError(f"Expected grid side length to be square. Actual side length {len(grid)}.")

		self._grid = grid
		self._solved_grid = copy.deepcopy(grid)
		self.side_length = len(grid)
		self.sub_side_length = int(maths.sqrt(self.side_length) + 0.5)
		self.number_set = set(range(1, self.side_length + 1))
		self._set_difficulty()
		print(f"DONE")

		print(f"SOLVING PUZZLE...", end=" ", flush=True)
		self.solve()
		print(f"DONE")

	def get_row(self, row):
		return tuple(self._solved_grid[row])

	def get_column(self, column):
		return tuple(x[column] for x in self._solved_grid)

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
		return self._solved_grid[row][column]

	def __set_tile(self, row, column, value, force=False):
		if value not in self.number_set and not force:
			raise ValueError(
				f"{value} is not a valid value in this puzzle. Valid values are: {', '.join(str(x) for x in self.number_set)}")
		if row >= self.side_length or column >= self.side_length:
			raise ValueError(f"{row}, {column} is not a valid position in a puzzle with side length {self.side_length}")
		self._solved_grid[row][column] = value

	def __set_subgrid_tile(self, sub_row, sub_col, row, column, value, force=False):
		"""
		Sets the value of a tile within a given subgrid.

		:param sub_row: The subgrid row.
		:param sub_col: The subgrid column.
		:param row: The row in the subgrid.
		:param column: The column in the subgrid.
		:param value: The value to set the tile to.
		:param force: Setting this flag to true suppresses the value is in the number set check.
		:return: None
		"""
		row_offset = sub_row * self.sub_side_length
		column_offset = sub_col * self.sub_side_length
		if sub_row >= self.sub_side_length or sub_col >= self.sub_side_length or sub_row < 0 or sub_col < 0:
			raise ValueError(
				f"{sub_row}, {sub_col} is not a valid position in a subgrid with side length {self.sub_side_length}")
		if row >= self.sub_side_length or column >= self.sub_side_length or row < 0 or column < 0:
			raise ValueError(
				f"{row}, {column} is not a valid subgrid position in a puzzle with side length {self.side_length} and sub side length {self.sub_side_length}")
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
		Checks that no value is repeated in a row, column or subgrid (i.e. the 3x3 tiles in a 9x9 grid)
		and checks that all values are members of the number set or 0.

		:return: True if every value in evey row/column is unique in that row. False otherwise.
		"""
		valid = not self.contains_invalid_values()
		for i in range(self.side_length):
			# might need to double check that side length and length of number set is the same
			# * (puzzle is impossible if number set is shorter)
			# * (puzzle is wrong if number set is longer)
			valid = valid and len(set(self.get_row(i))) == self.side_length
			valid = valid and len(set(self.get_column(i))) == self.side_length
			valid = valid and len(set(
				[x
				 for r in range(0, self.side_length, self.sub_side_length)
				 for c in range(0, self.side_length, self.sub_side_length)
				 for y in self.get_subgrid(r, c)
				 for x in y])) == self.side_length

		return valid

	def is_complete(self):
		"""
		Checks that all the values in the grid are members of the number set
		and that all values in a row/column/subgrid are unique to each other.
		The combination of these checks is sufficient to say whether the puzzle is complete.

		:return: True if the puzzle is complete. False otherwise.
		"""
		return self.is_full() and self.is_valid()

	def contains_invalid_values(self):
		"""
		Checks that the puzzle doesn't contain values that are not members of its number set
		or the empty placeholder value 0.

		:return: True if the puzzle contains values it shouldn't. False otherwise.
		"""
		invalid = False
		for i in range(self.side_length):
			invalid = invalid or any([x not in set.union(self.number_set, {0}) for x in self.get_row(i)])
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
		self._solved_grid = copy.deepcopy(self._grid)

	def _set_difficulty(self):
		self.difficulty = None  # todo

	def solve(self):
		change_made = False

		def get_valid_positions(value, subgrid_row, subgrid_col):
			"""
			This method returns the valid positions of a given value in a given subgrid.

			:param value: The value to find the valid positions for.
			:param subgrid_row: The row value of the top left corner of the subgrid being searched.
			:param subgrid_col: The column value of the top left corner of the subgrid being searched.
			:return: A set of (r,c) tuples which are valid positions for the value to be placed in.
			"""
			valid_positions = set([(x, y) for x in range(self.sub_side_length) for y in range(self.sub_side_length) if
								   not self.get_tile(x + subgrid_row, y + subgrid_col)])
			for i in range(self.sub_side_length):
				if value in self.get_row(subgrid_row + i):
					valid_positions = valid_positions.difference([(i, x) for x in range(self.sub_side_length)])
				if value in self.get_column(subgrid_col + i):
					valid_positions = valid_positions.difference([(x, i) for x in range(self.sub_side_length)])
			if len(valid_positions) == 0:
				raise Exception(
					f"Unable to find valid positions for {value} in subgrid with top left tile row: {subgrid_row} column: {subgrid_col}.")
			return valid_positions

		def fill_known_subgrid_values():
			"""
			This method checks the valid positions of each number in each subgrid.
			If there is only one valid position the number will be placed in it.

			:return: None
			"""
			nonlocal change_made
			for r in range(0, self.side_length, self.sub_side_length):
				for c in range(0, self.side_length, self.sub_side_length):
					unplaced_number_set = self.number_set.difference(
						[x for y in self.get_subgrid(r, c) for x in y if x in self.number_set])
					for n in unplaced_number_set:
						valid_places = get_valid_positions(n, r, c)
						if len(valid_places) == 1:
							place = valid_places.pop()
							del valid_places
							self.__set_tile(r + place[0], c + place[1], n)
							change_made = True

		def fill_singleton_possibilities():
			"""
			This method iterates over each tile and applies a set of possible values to the tile based on
			what is in the same subgrid, row and column as that tile. If the set of values is a singleton then
			the singleton value is placed in the tile.

			:return: None
			"""
			nonlocal change_made
			for r in range(self.side_length):
				for c in range(self.side_length):
					if not self.get_tile(r, c):
						# (c,r) are the coordinates of a single empty tile
						possible_number_set = self.number_set.difference(
							[x for y in self.get_subgrid(r, c) for x in y if x in self.number_set])
						possible_number_set = possible_number_set.difference(
							[x for x in self.get_row(r) if x in self.number_set])
						possible_number_set = possible_number_set.difference(
							[x for x in self.get_column(c) if x in self.number_set])

						if len(possible_number_set) == 0:
							raise Exception(f"Unable to place a value in row: {r} column {c}. It is impossible")
						elif len(possible_number_set) == 1:
							self.__set_tile(r, c, possible_number_set.pop())
							change_made = True

		def fill_known_row_column_values():
			"""
			This method checks the valid positions of each number in each row/column.
			If there is only one valid position the number will be placed in it.

			:return: None
			"""
			nonlocal change_made
			for n in self.number_set:
				for i in range(self.side_length):
					# * n = a value from the number set
					# * i = an index along the row/column
					if n not in self.get_row(i):
						# take all indexes in the row
						valid_row_indexes = set(range(self.side_length))
						# remove indexes where there is already a value
						valid_row_indexes = valid_row_indexes.difference(
							[x for x in range(self.side_length) if self.get_row(i)[x] in self.number_set])
						# remove indexes where n conflicts with itself in that column
						valid_row_indexes = valid_row_indexes.difference(
							[x for x in range(self.side_length) if n in self.get_column(x)])
						# remove indexes where n conflicts with itself in that subgrid
						valid_row_indexes = valid_row_indexes.difference(
							[x for x in range(self.side_length) if n in [y for z in self.get_subgrid(i, x) for y in z]])
						if len(valid_row_indexes) == 0:
							raise Exception(f"Unable to place {n} in row: {i}. It is impossible")
						elif len(valid_row_indexes) == 1:
							index = valid_row_indexes.pop()
							self.__set_tile(i, index, n)
							change_made = True

					if n not in self.get_column(i):
						# take all indexes in the column
						valid_column_indexes = set(range(self.side_length))
						# remove indexes where there is already a value
						valid_column_indexes = valid_column_indexes.difference(
							[x for x in range(self.side_length) if self.get_column(i)[x] in self.number_set])
						# remove indexes where n conflicts with itself in that column
						valid_column_indexes = valid_column_indexes.difference(
							[x for x in range(self.side_length) if n in self.get_row(x)])
						# remove indexes where n conflicts with itself in that subgrid
						valid_column_indexes = valid_column_indexes.difference(
							[x for x in range(self.side_length) if n in [y for z in self.get_subgrid(x, i) for y in z]])
						if len(valid_column_indexes) == 0:
							raise Exception(f"Unable to place {n} in column: {i}. It is impossible")
						elif len(valid_column_indexes) == 1:
							index = valid_column_indexes.pop()
							self.__set_tile(index, i, n)  # probably where the error is
							change_made = True

		def fill_based_on_multiple_value_possibilities():
			nonlocal change_made
			for r in range(0, self.side_length, self.sub_side_length):
				for c in range(0, self.side_length, self.sub_side_length):
					# r is the subgrid row number
					# c is the subgrid column number
					# both go up in steps of self.sub_side_length
					def fill_multiple_value_tiles():
						position_map = {}
						unplaced_number_set = self.number_set.difference(
							[x for y in self.get_subgrid(r, c) for x in y if isinstance(x, int)])
						unplaced_number_set = unplaced_number_set.difference(
							[x for y in self.get_subgrid(r, c) for z in y if isinstance(z, set) for x in z])
						for n in unplaced_number_set:
							valid_places = get_valid_positions(n, r, c)
							position_map.update({n: valid_places})
						for n, p in position_map.items():
							identical_list = [x for x in position_map.items() if x[1] == p]
							if len(identical_list) > 1 and len(identical_list) == len(identical_list[0][1]):
								for i in identical_list[0][1]:
									self.__set_tile(r + i[0], c + i[1], set([x for x, _ in identical_list]), force=True)
								fill_multiple_value_tiles()
								break

					def clear_multiple_value_tiles():
						for i in range(0, self.sub_side_length, 1):
							for j in range(0, self.sub_side_length, 1):
								if isinstance(self.get_tile(r + i, c + j), set):
									self.__set_tile(r + i, c + j, 0, force=True)

					fill_multiple_value_tiles()

					unplaced_number_set = self.number_set.difference(
						[x for y in self.get_subgrid(r, c) for x in y if x in self.number_set])
					unplaced_number_set = unplaced_number_set.difference(
						[x for y in self.get_subgrid(r, c) for z in y if isinstance(z, set) for x in z])
					for n in unplaced_number_set:
						valid_places = get_valid_positions(n, r, c)
						if len(valid_places) == 1:
							place = valid_places.pop()
							del valid_places
							self.__set_tile(r + place[0], c + place[1], n)
							change_made = True

					if not self.get_tile(r, c):
						# (c,r) are the coordinates of a single empty tile
						possible_number_set = self.number_set.difference(
							[x for y in self.get_subgrid(r, c) for x in y if x in self.number_set])
						possible_number_set = possible_number_set.difference(
							[x for y in self.get_subgrid(r, c) for z in y if isinstance(z, set) for x in z])
						possible_number_set = possible_number_set.difference(
							[x for x in self.get_row(r) if x in self.number_set])
						possible_number_set = possible_number_set.difference(
							[x for x in self.get_column(c) if x in self.number_set])

						if len(possible_number_set) == 0:
							raise Exception(f"Unable to place a value in row: {r} column {c}. It is impossible")
						elif len(possible_number_set) == 1:
							self.__set_tile(r, c, possible_number_set.pop())
							change_made = True

					clear_multiple_value_tiles()

		if self.contains_invalid_values():
			raise Exception("The puzzle that is trying to be solved is invalid and will not have a solution.")

		fill_known_subgrid_values()
		if self.is_complete():
			# print("SOLVED")
			return None
		fill_singleton_possibilities()
		if self.is_complete():
			# print("SOLVED")
			return None
		fill_known_row_column_values()
		if self.is_complete():
			# print("SOLVED")
			return None
		if not change_made:
			fill_based_on_multiple_value_possibilities()
			if self.is_complete():
				return None

		if not change_made:
			raise Exception("The solving algorithm has insufficient ability to solve this puzzle.")
		else:
			self.solve()

	def get_as_serialized_dict(self):
		data = {
			"side length": self.side_length,
			"difficulty": self.difficulty,
			"grid": self._grid,
			"solved grid": self._solved_grid
		}
		return data

	def set_from_serialised_dict(self, data):
		self.__set_grid(data["grid"])


def main():
	puzzles_data = {"puzzles": []}

	def add_to_puzzles(new_puzzle):
		if isinstance(new_puzzle, SudokuPuzzle):
			puzzles_data["puzzles"].append(new_puzzle.get_as_serialized_dict())
		else:
			raise TypeError(f"{new_puzzle} is not an object of type {SudokuPuzzle} and cannot be as such.")

	unsolveable_grid = [
		[0, 0, 3, 2, 0, 0, 0, 0, 0],
		[0, 4, 7, 0, 1, 0, 0, 0, 6],
		[0, 0, 5, 0, 0, 4, 0, 0, 0],
		[0, 7, 0, 0, 5, 0, 0, 0, 0],
		[6, 2, 0, 0, 0, 0, 0, 1, 4],
		[0, 0, 0, 0, 8, 0, 0, 3, 0],
		[0, 0, 0, 3, 0, 0, 8, 0, 0],
		[9, 0, 0, 0, 6, 0, 7, 4, 0],
		[0, 0, 0, 0, 0, 5, 6, 0, 0]
	]

	grid = [
		[0, 0, 0, 0, 6, 0, 0, 7, 4],
		[0, 0, 0, 2, 4, 5, 0, 0, 0],
		[0, 0, 2, 0, 0, 0, 0, 0, 5],
		[6, 0, 0, 0, 2, 4, 1, 0, 0],
		[0, 2, 9, 0, 5, 0, 7, 8, 0],
		[0, 0, 8, 3, 7, 0, 0, 0, 2],
		[3, 0, 0, 0, 0, 0, 4, 0, 0],
		[0, 0, 0, 6, 3, 8, 0, 0, 0],
		[8, 7, 0, 0, 1, 0, 0, 0, 0]
	]

	serial = {
		"side length": 9,
		"difficulty": None,
		"grid": unsolveable_grid,
		"solved grid": []
	}
	puzzle = SudokuPuzzle()
	try:
		puzzle.set_from_serialised_dict(serial)
	except:
		print(f"fail!!!")

	# with open("PuzzleExample.json", "rt") as json_in:
	#	puzzles_data = json.load(json_in)
	#	for p in puzzles_data["puzzles"]:
	#		puzzle = SudokuPuzzle()
	#		puzzle.set_from_serialised_dict(p)
	#		puzzle.solve()
	#		for i in range(puzzle.side_length):
	#			print(puzzle.get_row(i))
	#		print(f"\n\n")
	#		for i in range(puzzle.side_length):
	#			print(puzzle._grid[i])
	#
	#	del puzzles_data

	with open("PuzzleExample.json", "wt") as json_out:
		add_to_puzzles(puzzle)
		json.dump(puzzles_data, json_out, indent=4, separators=(", ", ": "))


if __name__ == "__main__": main()
