import os
from generate_pdf import generate_pdf

game_front_directory = os.path.join('game', 'front')
game_back_directory = os.path.join('game', 'back')
output_directory = os.path.join('game', 'output')

back_filename = 'back.jpg'
back_path = os.path.join(game_back_directory, back_filename)

pdf_path = os.path.join(output_directory, 'card_game.pdf')

enable_front_registration = False

generate_pdf(game_front_directory, back_path, pdf_path)