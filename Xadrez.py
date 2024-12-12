import pygame
from sys import exit
import os

pygame.init()

# Game constants
SCREEN_SIZE = 600
SCREEN_TITLE = "Xadrez"
BOARD_SIZE = 8
SQUARE_SIZE = SCREEN_SIZE / BOARD_SIZE
BOARD_COLOR_1 = (240, 217, 181)
BOARD_COLOR_2 = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)
MOVE_INDICATOR_COLOR = (119, 149, 86)

class ChessGame:
    def __init__(self):
        """Initialize the chess game."""
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption(SCREEN_TITLE)
        self.selected_piece = None
        self.selected_pos = None
        self.turn = 'b'
        self.possible_moves = []
        self.check = {'b': False, 'p': False}
        self.king_positions = {'b': (7, 4), 'p': (0, 4)}
        self.capturable_pieces = set()
        self.game_over = False
        self.winner = None
        self.font = pygame.font.SysFont('Arial', 48)
        self.load_pieces()
        self.init_board()
        self.promoting_pawn = None
        self.promotion_options = ['D', 'T', 'B', 'C']

    def load_pieces(self):
        """Load images for chess pieces."""
        def load_image(path):
            if not os.path.isfile(path):
                raise FileNotFoundError(f"No file '{path}' found in working directory '{os.getcwd()}'")
            return pygame.transform.scale(pygame.image.load(path), (int(SQUARE_SIZE), int(SQUARE_SIZE)))

        self.black_pieces = {
            'Pp': load_image('projectXadrez/pecas_pretas/pawn1.png'),
            'Tp': load_image('projectXadrez/pecas_pretas/rook1.png'),
            'Cp': load_image('projectXadrez/pecas_pretas/knight1.png'),
            'Bp': load_image('projectXadrez/pecas_pretas/bishop1.png'),
            'Dp': load_image('projectXadrez/pecas_pretas/queen1.png'),
            'Rp': load_image('projectXadrez/pecas_pretas/king1.png')
        }

        self.white_pieces = {
            'Pb': load_image('projectXadrez/pecas_brancas/pawn.png'),
            'Tb': load_image('projectXadrez/pecas_brancas/rook.png'),
            'Cb': load_image('projectXadrez/pecas_brancas/knight.png'),
            'Bb': load_image('projectXadrez/pecas_brancas/bishop.png'),
            'Db': load_image('projectXadrez/pecas_brancas/queen.png'),
            'Rb': load_image('projectXadrez/pecas_brancas/king.png')
        }

    def init_board(self):
        """Initialize the chess board with starting positions."""
        self.board = [
            ['Tp', 'Cp', 'Bp', 'Dp', 'Rp', 'Bp', 'Cp', 'Tp'],
            ['Pp'] * 8,
            ['  '] * 8,
            ['  '] * 8,
            ['  '] * 8,
            ['  '] * 8,
            ['Pb'] * 8,
            ['Tb', 'Cb', 'Bb', 'Db', 'Rb', 'Bb', 'Cb', 'Tb']
        ]

    def is_valid_move(self, start_pos, end_pos):
        """Check if a move is valid."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.board[start_row][start_col].strip()
        
        if piece[1] != self.turn:
            return False

        end_piece = self.board[end_row][end_col].strip()
        if end_piece and end_piece[1] == piece[1]:
            return False

        piece_type = piece[0]
        if piece_type == 'P':
            if piece[1] == 'b':
                if end_col == start_col and end_row == start_row - 1 and not end_piece:
                    return True
                if start_row == 6 and end_col == start_col and end_row == start_row - 2:
                    return not end_piece and not self.board[start_row - 1][start_col].strip()
                if end_row == start_row - 1 and abs(end_col - start_col) == 1 and end_piece:
                    return True
            else:
                if end_col == start_col and end_row == start_row + 1 and not end_piece:
                    return True
                if start_row == 1 and end_col == start_col and end_row == start_row + 2:
                    return not end_piece and not self.board[start_row + 1][start_col].strip()
                if end_row == start_row + 1 and abs(end_col - start_col) == 1 and end_piece:
                    return True
            return False

        return (end_row, end_col) in self.get_possible_moves((start_row, start_col))

    def is_king_in_check(self, color, ignore_piece=None):
        """Check if the king of the given color is in check."""
        king_pos = self.king_positions[color]
        opponent_color = 'p' if color == 'b' else 'b'
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col].strip()
                if piece and piece[1] == opponent_color:
                    if ignore_piece and (row, col) == ignore_piece:
                        continue
                    moves = self.get_basic_moves((row, col))
                    if king_pos in moves:
                        return True
        return False

    def move_piece(self, start_pos, end_pos):
        """Move a piece from start_pos to end_pos if the move is valid."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.board[start_row][start_col].strip()
        
        if not self.is_valid_move(start_pos, end_pos):
            return False
            
        old_board = [row[:] for row in self.board]
        old_king_pos = self.king_positions.copy()
        
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = '  '
        
        if piece[0] == 'R':
            self.king_positions[piece[1]] = (end_row, end_col)
        
        if self.is_king_in_check(piece[1]):
            self.board = [row[:] for row in old_board]
            self.king_positions = old_king_pos.copy()
            return False
        
        opponent_color = 'p' if piece[1] == 'b' else 'b'
        self.check[opponent_color] = self.is_king_in_check(opponent_color)
        self.check['b'] = self.is_king_in_check('b')
        self.check['p'] = self.is_king_in_check('p')
        
        if self.check[opponent_color] and self.is_checkmate(opponent_color):
            self.game_over = True
            self.winner = 'Brancas' if piece[1] == 'b' else 'Pretas'
        
        if piece[0] == 'P' and (end_row == 0 or end_row == 7):
            self.promoting_pawn = (end_row, end_col)
        else:
            self.turn = opponent_color
            
        return True

    def get_moves_to_escape_check(self, color):
        """Return moves that can remove the king from check."""
        valid_moves = []
        king_row, king_col = self.king_positions[color]
        
        king_piece = self.board[king_row][king_col]
        moves = self.get_basic_moves((king_row, king_col))
        
        for move in moves:
            old_board = [row[:] for row in self.board]
            old_king_pos = self.king_positions.copy()
            
            self.board[move[0]][move[1]] = king_piece
            self.board[king_row][king_col] = '  '
            self.king_positions[color] = move
            
            if not self.is_king_in_check(color):
                valid_moves.append((king_row, king_col, move[0], move[1]))
            
            self.board = [row[:] for row in old_board]
            self.king_positions = old_king_pos.copy()
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col].strip()
                if piece and piece[1] == color and piece[0] != 'R':
                    moves = self.get_basic_moves((row, col))
                    for move_row, move_col in moves:
                        old_board = [row[:] for row in self.board]
                        self.board[move_row][move_col] = piece
                        self.board[row][col] = '  '
                        
                        if not self.is_king_in_check(color):
                            valid_moves.append((row, col, move_row, move_col))
                        
                        self.board = [row[:] for row in old_board]
        
        return valid_moves

    def get_basic_moves(self, pos):
        """Return basic moves for a piece without considering check."""
        row, col = pos
        piece = self.board[row][col].strip()
        moves = []
        
        if not piece:
            return moves

        piece_type = piece[0]
        is_white = piece[1] == 'b'

        if piece_type == 'P':
            direction = -1 if is_white else 1
            next_row = row + direction
            if 0 <= next_row < BOARD_SIZE and self.board[next_row][col].strip() == '':
                moves.append((next_row, col))
                if ((is_white and row == 6) or (not is_white and row == 1)):
                    double_row = row + 2 * direction
                    if 0 <= double_row < BOARD_SIZE and self.board[double_row][col].strip() == '':
                        moves.append((double_row, col))
            
            for dc in [-1, 1]:
                next_col = col + dc
                if 0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE:
                    target = self.board[next_row][next_col].strip()
                    if target and target[1] != piece[1]:
                        moves.append((next_row, next_col))

        elif piece_type == 'T':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    next_row, next_col = row + dr * i, col + dc * i
                    if not (0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE):
                        break
                    target = self.board[next_row][next_col].strip()
                    if target == '':
                        moves.append((next_row, next_col))
                    elif target[1] != piece[1]:
                        moves.append((next_row, next_col))
                        break
                    else:
                        break

        elif piece_type == 'C':
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                          (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                next_row, next_col = row + dr, col + dc
                if 0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE:
                    target = self.board[next_row][next_col].strip()
                    if target == '' or target[1] != piece[1]:
                        moves.append((next_row, next_col))

        elif piece_type == 'B':
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    next_row, next_col = row + dr * i, col + dc * i
                    if not (0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE):
                        break
                    target = self.board[next_row][next_col].strip()
                    if target == '':
                        moves.append((next_row, next_col))
                    elif target[1] != piece[1]:
                        moves.append((next_row, next_col))
                        break
                    else:
                        break

        elif piece_type == 'D':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                        (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    next_row, next_col = row + dr * i, col + dc * i
                    if not (0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE):
                        break
                    target = self.board[next_row][next_col].strip()
                    if target == '':
                        moves.append((next_row, next_col))
                    elif target[1] != piece[1]:
                        moves.append((next_row, next_col))
                        break
                    else:
                        break

        elif piece_type == 'R':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                        (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                next_row, next_col = row + dr, col + dc
                if 0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE:
                    target = self.board[next_row][next_col].strip()
                    if target == '' or target[1] != piece[1]:
                        moves.append((next_row, next_col))

        return moves

    def would_expose_king(self, start_pos, end_pos):
        """Check if a move would expose the king to check."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.board[start_row][start_col].strip()
        color = piece[1]
        
        old_piece = self.board[end_row][end_col]
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = '  '
        
        old_king_pos = None
        if piece[0] == 'R':
            old_king_pos = self.king_positions[color]
            self.king_positions[color] = (end_row, end_col)
        
        exposed = self.is_king_in_check(color, ignore_piece=(end_row, end_col))
        
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = old_piece
        if old_king_pos:
            self.king_positions[color] = old_king_pos
        
        return exposed

    def get_possible_moves(self, pos, check_for_check=True):
        """Return possible moves considering check if check_for_check=True."""
        row, col = pos
        piece = self.board[row][col].strip()
        
        if check_for_check and self.check[self.turn] and piece[1] == self.turn:
            valid_moves = self.get_moves_to_escape_check(self.turn)
            moves = []
            for start_row, start_col, end_row, end_col in valid_moves:
                if start_row == row and start_col == col:
                    moves.append((end_row, end_col))
            return moves
        
        moves = self.get_basic_moves(pos)
        
        if not check_for_check:
            return moves
            
        valid_moves = []
        for move in moves:
            if not self.would_expose_king((row, col), move):
                valid_moves.append(move)
                
        return valid_moves

    def get_capturable_pieces(self, pos):
        """Return set of positions of pieces that can be captured by the selected piece."""
        row, col = pos
        piece = self.board[row][col].strip()
        capturable = set()
        
        if piece and piece[1] == self.turn:
            moves = self.get_possible_moves((row, col))
            for move_row, move_col in moves:
                target = self.board[move_row][move_col].strip()
                if target:
                    capturable.add((move_row, move_col))
        
        return capturable

    def update_capturable_pieces(self):
        """Update the set of capturable pieces."""
        self.capturable_pieces.clear()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col].strip()
                if piece and piece[1] == self.turn:
                    moves = self.get_possible_moves((row, col))
                    for move_row, move_col in moves:
                        target = self.board[move_row][move_col].strip()
                        if target:
                            self.capturable_pieces.add((move_row, move_col))

    def is_checkmate(self, color):
        """Check if the given color is in checkmate."""
        if not self.check[color]:
            return False
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col].strip()
                if piece and piece[1] == color:
                    moves = self.get_possible_moves((row, col))
                    for move in moves:
                        old_board = [row[:] for row in self.board]
                        old_king_pos = self.king_positions.copy()
                        
                        self.board[move[0]][move[1]] = piece
                        self.board[row][col] = '  '
                        if piece[0] == 'R':
                            self.king_positions[color] = move
                        
                        if not self.is_king_in_check(color):
                            self.board = [row[:] for row in old_board]
                            self.king_positions = old_king_pos.copy()
                            return False
                        
                        self.board = [row[:] for row in old_board]
                        self.king_positions = old_king_pos.copy()
        return True

    def draw_move_indicators(self):
        """Draw indicators for possible moves."""
        for move in self.possible_moves:
            row, col = move
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            radius = SQUARE_SIZE // 6
            pygame.draw.circle(self.screen, MOVE_INDICATOR_COLOR, (center_x, center_y), radius)

    def draw_board(self):
        """Draw the chess board."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = BOARD_COLOR_1 if (row + col) % 2 == 0 else BOARD_COLOR_2
                pygame.draw.rect(self.screen, color,
                               (SQUARE_SIZE * col, SQUARE_SIZE * row, SQUARE_SIZE, SQUARE_SIZE))
                
                if self.selected_pos == (row, col):
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                    s.set_alpha(128)
                    s.fill(HIGHLIGHT_COLOR)
                    self.screen.blit(s, (SQUARE_SIZE * col, SQUARE_SIZE * row))
        self.draw_move_indicators()

    def draw_pieces(self):
        """Draw the chess pieces on the board."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col].strip()
                if piece:
                    if piece[1] == 'p':
                        piece_surface = self.black_pieces[piece].copy()
                    else:
                        piece_surface = self.white_pieces[piece].copy()
                    
                    if piece[0] == 'R':
                        if (piece[1] == 'b' and self.check['b']) or (piece[1] == 'p' and self.check['p']):
                            pygame.draw.rect(piece_surface, (255, 0, 0), 
                                          piece_surface.get_rect(), 3)
                    elif (row, col) in self.capturable_pieces:
                        pygame.draw.rect(piece_surface, (0, 255, 0), 
                                      piece_surface.get_rect(), 3)
                    
                    self.screen.blit(piece_surface,
                                   (SQUARE_SIZE * col, SQUARE_SIZE * row))

    def draw_checkmate_screen(self):
        """Draw the checkmate screen if the game is over."""
        if self.game_over:
            overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            text = self.font.render(f'Checkmate! {self.winner} vencem!', True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_SIZE/2, SCREEN_SIZE/2))
            self.screen.blit(text, text_rect)

    def is_promotion_position(self, pos, piece):
        """Check if a pawn is in promotion position."""
        row, _ = pos
        return (piece[0] == 'P' and 
                ((piece[1] == 'b' and row == 0) or 
                 (piece[1] == 'p' and row == 7)))

    def draw_promotion_screen(self):
        """Draw the promotion screen if a pawn is being promoted."""
        if not self.promoting_pawn:
            return
            
        row, col = self.promoting_pawn
        color = 'b' if self.board[row][col][1] == 'b' else 'p'
        
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        option_size = SQUARE_SIZE
        start_x = SCREEN_SIZE // 2 - (2 * option_size)
        start_y = SCREEN_SIZE // 2 - (option_size // 2)
        
        for i, piece_type in enumerate(self.promotion_options):
            piece_key = piece_type + color
            piece_img = self.white_pieces[piece_key] if color == 'b' else self.black_pieces[piece_key]
            
            bg_color = BOARD_COLOR_1 if i % 2 == 0 else BOARD_COLOR_2
            pygame.draw.rect(self.screen, bg_color,
                           (start_x + i * option_size, start_y, option_size, option_size))
            
            self.screen.blit(piece_img, (start_x + i * option_size, start_y))

    def promote_pawn(self, choice):
        """Promote a pawn to the chosen piece."""
        if not self.promoting_pawn:
            return
            
        row, col = self.promoting_pawn
        color = self.board[row][col][1]
        self.board[row][col] = choice + color
        self.promoting_pawn = None
        
        self.check['b'] = self.is_king_in_check('b')
        self.check['p'] = self.is_king_in_check('p')
        
        opponent_color = 'p' if color == 'b' else 'b'
        if self.check[opponent_color] and self.is_checkmate(opponent_color):
            self.game_over = True
            self.winner = 'Brancas' if color == 'b' else 'Pretas'

    def run(self):
        """Run the main game loop."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    col = int(pos[0] // SQUARE_SIZE)
                    row = int(pos[1] // SQUARE_SIZE)
                    
                    if self.promoting_pawn:
                        option_size = SQUARE_SIZE
                        start_x = SCREEN_SIZE // 2 - (2 * option_size)
                        start_y = SCREEN_SIZE // 2 - (option_size // 2)
                        
                        if start_y <= pos[1] <= start_y + option_size:
                            if start_x <= pos[0] <= start_x + 4 * option_size:
                                choice_idx = int((pos[0] - start_x) // option_size)
                                if 0 <= choice_idx < len(self.promotion_options):
                                    self.promote_pawn(self.promotion_options[choice_idx])
                                    self.turn = 'p' if self.turn == 'b' else 'b'
                        continue

                    if self.selected_piece:
                        moved = False
                        if (row, col) in self.possible_moves:
                            moved = self.move_piece(self.selected_pos, (row, col))
                        
                        if moved:
                            self.selected_piece = None
                            self.selected_pos = None
                            self.possible_moves = []
                            self.capturable_pieces.clear()
                        else:
                            piece = self.board[row][col].strip()
                            if piece and piece[1] == self.turn:
                                self.selected_piece = piece
                                self.selected_pos = (row, col)
                                self.possible_moves = self.get_possible_moves((row, col))
                                self.capturable_pieces = self.get_capturable_pieces((row, col))
                            else:
                                self.selected_piece = None
                                self.selected_pos = None
                                self.possible_moves = []
                                self.capturable_pieces.clear()
                    else:
                        piece = self.board[row][col].strip()
                        if piece and piece[1] == self.turn:
                            self.selected_piece = piece
                            self.selected_pos = (row, col)
                            self.possible_moves = self.get_possible_moves((row, col))
                            self.capturable_pieces = self.get_capturable_pieces((row, col))

            self.draw_board()
            self.draw_pieces()
            if self.promoting_pawn:
                self.draw_promotion_screen()
            elif self.game_over:
                self.draw_checkmate_screen()
            pygame.display.update()

if __name__ == '__main__':
    game = ChessGame()
    game.run()
