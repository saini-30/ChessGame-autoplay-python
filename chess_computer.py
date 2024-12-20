import pygame
import sys
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

def show_start_message():
    screen.fill(WHITE)  # Fill the screen with white or any background color
    font = pygame.font.SysFont("Arial", 60, bold=True, italic=True)  # Bold and Italic font
    text = font.render("Game Start", True, (0, 0, 255))  # Blue color
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()  # Update the screen
    pygame.time.wait(2000)  # Wait for 2 seconds

# Chess piece class
class ChessPiece:
    def __init__(self, color, type, image):
        self.color = color
        self.type = type
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (SQUARE_SIZE, SQUARE_SIZE))
        self.has_moved = False

# Initialize the board
board = [[None for _ in range(8)] for _ in range(8)]

# Current Player
current_player = 'white'  # Ensure current_player is initialized here

# Selected piece
selected_piece = None
selected_pos = None

def init_board():
    # Pawns
    for col in range(8):
        board[1][col] = ChessPiece('black', 'pawn', 'images/black_pawn.png')
        board[6][col] = ChessPiece('white', 'pawn', 'images/white_pawn.png')
    # Rooks
    board[0][0] = board[0][7] = ChessPiece('black', 'rook', 'images/black_rook.png')
    board[7][0] = board[7][7] = ChessPiece('white', 'rook', 'images/white_rook.png')
    # Knights
    board[0][1] = board[0][6] = ChessPiece('black', 'knight', 'images/black_knight.png')
    board[7][1] = board[7][6] = ChessPiece('white', 'knight', 'images/white_knight.png')
    # Bishops
    board[0][2] = board[0][5] = ChessPiece('black', 'bishop', 'images/black_bishop.png')
    board[7][2] = board[7][5] = ChessPiece('white', 'bishop', 'images/white_bishop.png')
    # Queens
    board[0][3] = ChessPiece('black', 'queen', 'images/black_queen.png')
    board[7][3] = ChessPiece('white', 'queen', 'images/white_queen.png')
    # Kings
    board[0][4] = ChessPiece('black', 'king', 'images/black_king.png')
    board[7][4] = ChessPiece('white', 'king', 'images/white_king.png')

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    if selected_pos:
        pygame.draw.rect(screen, YELLOW, (selected_pos[1] * SQUARE_SIZE, selected_pos[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_piece():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                screen.blit(piece.image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def is_king_in_check_after_move(piece, start_row, start_col, end_row, end_col):
    # Temporarily move the piece
    original_piece = board[end_row][end_col]
    board[end_row][end_col] = piece
    board[start_row][start_col] = None

    # Check if the king is in check after the move
    in_check = is_king_in_check(piece.color)

    # Undo the move
    board[start_row][start_col] = piece
    board[end_row][end_col] = original_piece

    return in_check

def get_valid_moves(piece, row, col):
    moves = []
    if piece.type == 'pawn':
        direction = -1 if piece.color == 'white' else 1
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))
            if (piece.color == 'white' and row == 6) or (piece.color == 'black' and row == 1):
                if board[row + 2 * direction][col] is None:
                    moves.append((row + 2 * direction, col))
        for dc in [-1, 1]:
            if 0 <= row + direction < 8 and 0 <= col + dc < 8:
                if board[row + direction][col + dc] and board[row + direction][col + dc].color != piece.color:
                    moves.append((row + direction, col + dc))
    elif piece.type == 'rook':
        # Horizontal and vertical movement
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c]:
                    if board[r][c].color != piece.color:  # Can capture an opponent's piece
                        moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr
                c += dc
    elif piece.type == 'knight':
        # "L" shaped moves
        knight_moves = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if not board[r][c] or board[r][c].color != piece.color:
                    moves.append((r, c))
    elif piece.type == 'bishop':
        # Diagonal movement
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c]:
                    if board[r][c].color != piece.color:  # Can capture an opponent's piece
                        moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr
                c += dc
    elif piece.type == 'queen':
        # Combines rook and bishop movement
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c]:
                    if board[r][c].color != piece.color:  # Can capture an opponent's piece
                        moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr
                c += dc
    elif piece.type == 'king':
        # One square in any direction
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                # Temporarily move the king and check if it results in a check
                if not board[r][c] or board[r][c].color != piece.color:
                    if not is_king_in_check_after_move(piece, row, col, r, c):
                        moves.append((r, c))  # Add only safe moves
    return moves


def is_king_in_check(color):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color != color:  # Check against the opponent's pieces
                valid_moves = get_valid_moves(piece, row, col)
                for move in valid_moves:
                    if board[move[0]][move[1]] and board[move[0]][move[1]].type == 'king' and board[move[0]][move[1]].color == color:
                        return True
    return False

def check_game_over():
    # Check if either king has been captured
    white_king_found = black_king_found = False

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.type == 'king':
                if piece.color == 'white':
                    white_king_found = True
                if piece.color == 'black':
                    black_king_found = True

    if not white_king_found:
        print("Computer wins! White's king has been captured.")
        pygame.time.wait(2000)  # Wait before closing
        pygame.quit()
        sys.exit()

    if not black_king_found:
        print("Player wins! Black's king has been captured.")
        pygame.time.wait(2000)  # Wait before closing
        pygame.quit()
        sys.exit()

    return False  # Game is still ongoing
def handle_click(pos):
    global selected_piece, selected_pos, current_player

    row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
    piece = board[row][col]

    if selected_piece is None:
        if piece and piece.color == current_player:
            selected_piece = piece
            selected_pos = (row, col)
    else:
        if selected_pos != (row, col):
            if piece and piece.color == current_player:
                selected_piece = piece
                selected_pos = (row, col)
            else:
                if (row, col) in get_valid_moves(selected_piece, selected_pos[0], selected_pos[1]):
                    # Temporarily move the piece
                    original_piece = board[row][col]
                    board[row][col] = selected_piece
                    board[selected_pos[0]][selected_pos[1]] = None

                    if is_king_in_check(current_player):  # Check if the king is still in check
                        # Undo the move if it doesn't resolve the check
                        board[selected_pos[0]][selected_pos[1]] = selected_piece
                        board[row][col] = original_piece
                        print("Move not allowed: King remains in check.")
                    else:
                        # Complete the move
                        selected_piece.has_moved = True

                        # Promote the pawn if it reaches the last row
                        if selected_piece.type == 'pawn':
                            if (selected_piece.color == 'white' and row == 0) or (selected_piece.color == 'black' and row == 7):
                                board[row][col] = ChessPiece(selected_piece.color, 'queen', f'images/{selected_piece.color}_queen.png')

                        current_player = 'black' if current_player == 'white' else 'white'

                    selected_piece = None
                    selected_pos = None


def computer_move():
    valid_moves = []
    capture_moves = []
    
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == 'black':  # Only consider black pieces (computer's pieces)
                moves = get_valid_moves(piece, row, col)
                for move in moves:
                    target_piece = board[move[0]][move[1]]
                    if target_piece and target_piece.color == 'white':  # Check if the move captures a white piece
                        capture_moves.append((piece, (row, col), move))
                    else:
                        valid_moves.append((piece, (row, col), move))

    if capture_moves:
        piece, (start_row, start_col), (end_row, end_col) = random.choice(capture_moves)
    else:
        if valid_moves:
            piece, (start_row, start_col), (end_row, end_col) = random.choice(valid_moves)
        else:
            return False  # No valid move left

    board[end_row][end_col] = piece
    board[start_row][start_col] = None

    if check_game_over():
        return False  # End the game if a king is captured

    return True


def main():
    global current_player
    show_start_message()
    init_board()
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(pygame.mouse.get_pos())

        draw_board()
        draw_piece()

        if current_player == 'black':  # It's the computer's turn
            if computer_move():
                current_player = 'white'  # Switch back to player's turn

        pygame.display.flip()

if __name__ == "__main__":
    main()
