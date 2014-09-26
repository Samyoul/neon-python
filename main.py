__author__ = 'Samuel'

import pygame, random, time
from pygame.locals import *

def main():

	black = (0,0,0)
	very_dark_grey = (25,25,25)
	dark_grey = (100,100,100)
	light_grey = (200,200,200)
	white = (255,255,255)
	red = (255,0,0)
	green = (0,255,0)
	blue = (0,0,255)

	#settings
	boardDims = (50,30) #number of cells on board

	#pygame settings
	cellDims = (20,20) #number of pixels on cells
	framerate = 20
	colours = {0:black, 1:blue, 2:red, 3:white, 4:green}

	#pygame
	pygame.init()
	dims = (boardDims[0] * cellDims[0], boardDims[1] * cellDims[1])
	screen = pygame.display.set_mode(dims)

	background = pygame.Surface(dims)
	background.set_colorkey(black)

	foreground = pygame.Surface(dims)
	foreground.set_colorkey(black)

	score_lower = pygame.Surface(dims)
	score_lower.set_colorkey(black)

	score_upper = pygame.Surface(dims)
	score_upper.set_colorkey(black)

	layers = (
		{'surface': background, 'position': (0,0)},
		{'surface': foreground, 'position': (0,0)},
		{'surface': score_lower, 'position': (0,0)},
		{'surface': score_upper, 'position': (0,0)}
	)

	clock = pygame.time.Clock()
	pygame.display.set_caption('Neon Snake!')

	cell_x = int(boardDims[0]/2)
	cell_y = int(boardDims[1]/2)

	#create new board
	board = {}
	#iterates over x and y axis of the window
	for x in range(boardDims[0]):
		for y in range(boardDims[1]):
			board[(x,y)] = 0 #sets whole board to value 0

	class Food:
		def __init__(self, x_location, y_location):
			self.last_location = {'x':x_location, 'y':y_location}
			self.location = {'x':x_location, 'y':y_location}
		def set_location(self, x_location, y_location):
			self.last_location = {'x':self.location['x'], 'y':self.location['y']}
			self.location = {'x':x_location, 'y':y_location}

	class Snake:
		def __init__(self, board, x_location, y_location, length):
			self.last_location = {}
			self.location = {}
			self.length = length
			self.moving_direction = "right"
			for i in range(0, length):
				self.last_location[i] = {'x': x_location - i, 'y': y_location}
				self.location[i] = {'x': x_location - i, 'y': y_location}
				board[(self.location[i]['x'],self.location[i]['y'])] = 1

		def grow(self):
			self.length += 1
			self.last_location[self.length-1] = {'x': self.last_location[self.length-2]['x'] + 1, 'y': self.last_location[self.length-2]['y'] + 1}
			self.location[self.length-1] = {'x': self.location[self.length-2]['x'] + 1, 'y': self.location[self.length-2]['y'] + 1}

		def direction(self, direction:str):
			if (direction == "up") or (direction == "down") or (direction == "left") or (direction == "right"):
				self.moving_direction = direction
			else:
				raise ValueError("The 'direction' argument must be 'up', 'down', left or 'right' you passed %s"%direction)

		def move(self, board, x_location:int, y_location:int):
			for section_id, section_location in self.location.items():
				board[(self.location[section_id]['x'],self.location[section_id]['y'])] = 0
				if section_id == 0:
					self.last_location[section_id]['x'] = section_location['x']
					self.last_location[section_id]['y'] = section_location['y']
					self.location[section_id]['x'] = x_location
					self.location[section_id]['y'] = y_location
				else:
					self.last_location[section_id]['x'] = section_location['x']
					self.last_location[section_id]['y'] = section_location['y']
					self.location[section_id]['x'] = self.last_location[section_id-1]['x']
					self.location[section_id]['y'] = self.last_location[section_id-1]['y']
				board[(self.location[section_id]['x'],self.location[section_id]['y'])] = 1

	foodClass = Food
	food_limit = 1
	foods = []

	def create_message(message, size, colour, position):
		font = pygame.font.Font("C:\\Users\Samuel\Documents\My Dropbox\Python Projects\\2048 selfreplication\\assets\\fonts\FFFFORWA.TTF", size)
		text = font.render(message, True, colour)
		score_upper.blit(text,position)

	def create_message_centred(message, size, colour, surface_dimensions, offset=(0,0)):
		font = pygame.font.Font("C:\\Users\Samuel\Documents\My Dropbox\Python Projects\\2048 selfreplication\\assets\\fonts\FFFFORWA.TTF", size)
		text = font.render(message, True, colour)
		x_pos = int((surface_dimensions[0]/2) - (text.get_width() / 2)) + offset[0]
		y_pos = int((surface_dimensions[1]/2) - (text.get_height() / 2)) + offset[1]
		score_upper.blit(text,(x_pos, y_pos))

	def show_stats(moves, score, length):
		create_message("Moves: "+str(moves), 20, light_grey, (0,0))
		create_message("Score: "+str(score), 20, light_grey, (0,25))
		create_message("Snake length: "+str(length), 20, light_grey, (0,50))

	def blurSurface(surface, level):
		"""
		Blur the given surface by the given 'amount'. Only values 1 and greater are valid.  Value 1 = no blur.
		"""
		if level < 1.0:
			raise ValueError("Arg 'level' must be greater than 1.0, passed in value is %s"%level)
		scale = 1.0/float(level)
		surf_size = surface.get_size()
		scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
		surf = pygame.transform.smoothscale(surface, scale_size)
		surf = pygame.transform.smoothscale(surf, surf_size)
		return surf

	def blit_layers(layers:tuple):
		for layer in layers:
			screen.blit(layer['surface'], layer['position'])

	def spawn_food(board, boardDims, Food, food_limit, foods):
		if 0 == len(foods):
			for i in range(0, food_limit):
				foods.append(Food(random.randint(0,boardDims[0]-1), random.randint(0,boardDims[1]-1)))
		elif (food_limit > len(foods)) and (len(foods) > 0):
			for food in foods:
				food.set_location(random.randint(0,boardDims[0]-1), random.randint(0,boardDims[1]-1))
			foods.append(Food(random.randint(0,boardDims[0]-1), random.randint(0,boardDims[1]-1)))
		elif food_limit == len(foods):
			for food in foods:
				food.set_location(random.randint(0,boardDims[0]-1), random.randint(0,boardDims[1]-1))

		for food in foods:
			board[(food.last_location['x'], food.last_location['y'])] = 0
			board[(food.location['x'], food.location['y'])] = 2

	spawn_food(board, boardDims, foodClass, food_limit, foods)
	snake = Snake(board, cell_x, cell_y, 10)

	def game_loop(food_limit, cell_x, cell_y):
		change = (1,0)
		score = 0
		moves = 0
		running = 1
		while running:
			#wipe all our layers clean
			for layer in layers:
				layer['surface'].fill(black)

			#start looking for events
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					running = 0

				if event.type == KEYDOWN:
					if event.key == pygame.K_d:
						if snake.moving_direction != "left":
							change = (1,0)
							snake.direction('right')
					elif event.key == pygame.K_s:
						if snake.moving_direction != "up":
							change = (0,1)
							snake.direction('down')
					elif event.key == pygame.K_a:
						if snake.moving_direction != "right":
							change = (-1,0)
							snake.direction('left')
					elif event.key == pygame.K_w:
						if snake.moving_direction != "down":
							change = (0,-1)
							snake.direction('up')
					elif event.key == pygame.K_p:
						change = (0,0)

			#check if we moved
			if cell_x + change[0] != cell_x or cell_y + change[1] != cell_y:
				moves += 1

				if (cell_x + change[0]) > boardDims[0]-1:
					cell_x = 0
				elif (cell_x + change[0]) < 0:
					cell_x = boardDims[0]-1
				else:
					cell_x += change[0]

				if (cell_y + change[1]) > boardDims[1]-1:
					cell_y = 0
				elif (cell_y + change[1]) < 0:
					cell_y = boardDims[1]-1
				else:
					cell_y += change[1]

				#If we've ate something
				if board[(cell_x, cell_y)] == 2:
					score +=1
					if score % 100 == 0:
						food_limit +=1
					spawn_food(board, boardDims, foodClass, food_limit, foods)
					snake.grow()

				#If we've crashed
				if board[(cell_x, cell_y)] == 1:
					game_over_loop()

				snake.move(board, cell_x, cell_y)

			screen.fill(black)
			for cell in board:
				#adds cells dimensions and co-ordinates to object rectangle
				rectangle =  (cell[0]*cellDims[0], cell[1]* cellDims[1], cellDims[0], cellDims[1])
				#pygame draws the rectangle on the background using the relevant
				#colour and dimensions and co-ordinates outlined in 'rectangle'
				pygame.draw.rect(foreground, colours[board[cell]], rectangle)

			layers[0]['surface'] = blurSurface(foreground, 15)
			layers[2]['surface'] = blurSurface(score_upper, 100)

			show_stats(moves, score, snake.length)
			blit_layers(layers)
			pygame.display.update()
			clock.tick(framerate)

	def game_over_loop():
		ended = 1
		while ended:
			create_message_centred("You Died !!! :(", 50, red, dims)
			create_message_centred("Press any key to continue", 40, red, dims,(0,65))
			blit_layers(layers)
			pygame.display.update()
			time.sleep(1)

			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					quit()
				if event.type == KEYDOWN:
					game_loop(food_limit, cell_x, cell_y)

	game_loop(food_limit, cell_x, cell_y)

main()