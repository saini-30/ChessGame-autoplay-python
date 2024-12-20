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
LIGHT_YELLOW = (255, 255, 153)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Load piece images
PIECE_IMAGES = {
    "white_pawn": "images/white_pawn.png",
    "black_pawn": "images/black_pawn.png",
    "white_rook": "images/white_rook.png",
    "black_rook": "images/black_rook.png",
    "white_knight": "images/white_knight.png",
    "black_knight": "images/black_knight.png",
    "white_bishop": "images/white_bishop.png",
    "black_bishop": "images/black_bishop.png",
    "white_queen": "images/white_queen.png",
    "black_queen": "images/black_queen.png",
    "white_king": "images/white_king.png",
    "black_king": "images/black_king.png",
}

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

# Selected piece
selected_piece = None
selected_pos = None

# Current player
current_player = "white"

# Last move positions for highlighting
last_move_start = None
last_move_end = None

# Initialize game state
def init_board():
    """Set up the initial chessboard."""
    for col in range(8):
        board[1][col] = ChessPiece("black", "pawn", PIECE_IMAGES["black_pawn"])
        board[6][col] = ChessPiece("white", "pawn", PIECE_IMAGES["white_pawn"])

    pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for col, piece in enumerate(pieces):
        board[0][col] = ChessPiece("black", piece, PIECE_IMAGES[f"black_{piece}"])
        board[7][col] = ChessPiece("white", piece, PIECE_IMAGES[f"white_{piece}"])

# Draw the chessboard
def draw_board():
    """Draw the chessboard on the screen."""
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    if selected_pos:
        pygame.draw.rect(screen, YELLOW, (selected_pos[1] * SQUARE_SIZE, selected_pos[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

    if last_move_start:
        pygame.draw.rect(screen, LIGHT_YELLOW, (last_move_start[1] * SQUARE_SIZE, last_move_start[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    if last_move_end:
        pygame.draw.rect(screen, LIGHT_YELLOW, (last_move_end[1] * SQUARE_SIZE, last_move_end[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw pieces
def draw_pieces():
    """Draw chess pieces on the board."""
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                screen.blit(piece.image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Check if the king is in check
def is_king_in_check(board, player_color):
    king_pos = find_king(board, player_color)
    if not king_pos:
        return True  # King is captured
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color != player_color:
                if can_attack(piece, (row, col), king_pos, board):
                    return True
    return False

# Get the position of the king for the given player color
def find_king(board, player_color):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == player_color and piece.type == "king":
                return (row, col)
    return None

# Check if a piece can attack a target position
def can_attack(piece, piece_pos, target_pos, board):
    row, col = piece_pos
    target_row, target_col = target_pos

    if piece.type == "pawn":
        direction = -1 if piece.color == "white" else 1
        if (target_row == row + direction and target_col in [col - 1, col + 1]):
            return True
    elif piece.type == "rook":
        if row == target_row or col == target_col:
            return True
    elif piece.type == "knight":
        if (abs(row - target_row), abs(col - target_col)) in [(2, 1), (1, 2)]:
            return True
    elif piece.type == "bishop":
        if abs(row - target_row) == abs(col - target_col):
            return True
    elif piece.type == "queen":
        if row == target_row or col == target_col or abs(row - target_row) == abs(col - target_col):
            return True
    elif piece.type == "king":
        if max(abs(row - target_row), abs(col - target_col)) == 1:
            return True

    return False

# Get valid moves for a piece
def get_valid_moves(piece, row, col, board):
    """Return a list of valid moves for the given piece."""
    moves = []

    if piece.type == "pawn":
        direction = -1 if piece.color == "white" else 1
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))
            if not piece.has_moved and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))

        for dc in [-1, 1]:
            if 0 <= row + direction < 8 and 0 <= col + dc < 8:
                target = board[row + direction][col + dc]
                if target and target.color != piece.color:
                    moves.append((row + direction, col + dc))
    elif piece.type == 'rook':
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c]:
                    if board[r][c].color != piece.color:
                        moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr
                c += dc
    elif piece.type == 'knight':
        knight_moves = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if not board[r][c] or board[r][c].color != piece.color:
                    moves.append((r, c))
    elif piece.type == 'bishop':
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c]:
                    if board[r][c].color != piece.color:
                        moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr
                c += dc
    elif piece.type == 'queen':
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c]:
                    if board[r][c].color != piece.color:
                        moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr
                c += dc
    elif piece.type == 'king':
        king_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if not board[r][c] or board[r][c].color != piece.color:
                    moves.append((r, c))

    # Filter out moves that would leave the king in check
    valid_moves = []
    for move in moves:
        original_piece = board[move[0]][move[1]]
        board[move[0]][move[1]] = piece
        board[row][col] = None
        if not is_king_in_check(board, piece.color):
            valid_moves.append(move)
        board[row][col] = piece
        board[move[0]][move[1]] = original_piece

    return valid_moves

# Check if the current player is in checkmate
def is_checkmate(board, player_color):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == player_color:
                if get_valid_moves(piece, row, col, board):
                    return False
    return True

# Handle piece click (movement)
def handle_click(pos):
    global selected_piece, selected_pos, current_player, last_move_start, last_move_end

    col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
    piece = board[row][col]

    if selected_piece:
        if piece and piece.color == selected_piece.color:
            selected_pos = (row, col)
            selected_piece = piece
            return
        if (row, col) in get_valid_moves(selected_piece, selected_pos[0], selected_pos[1], board):
            last_move_start = selected_pos
            last_move_end = (row, col)
            board[row][col] = selected_piece
            board[selected_pos[0]][selected_pos[1]] = None
            selected_piece.has_moved = True
            if selected_piece.type == "pawn" and (row == 0 or row == 7):
                board[row][col] = ChessPiece(selected_piece.color, "queen", PIECE_IMAGES[f"{selected_piece.color}_queen"])
            if is_king_in_check(board, current_player):
                if is_checkmate(board, current_player):
                    print(f"{current_player.capitalize()} is in checkmate. Game over!")
                    pygame.quit()
                    sys.exit()
            current_player = "black" if current_player == "white" else "white"
            if current_player == "black":
                computer_move()
        else:
            print("Invalid move!")
        selected_piece = None
        selected_pos = None
    else:
        if piece and piece.color == current_player:
            selected_pos = (row, col)
            selected_piece = piece

# Computer move logic
def computer_move():
    global current_player, last_move_start, last_move_end
    valid_moves = []

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == "black":
                moves = get_valid_moves(piece, row, col, board)
                for move in moves:
                    valid_moves.append((piece, (row, col), move))

    if valid_moves:
        # Prioritize capturing moves
        capture_moves = [(piece, start_pos, end_pos) for piece, start_pos, end_pos in valid_moves if board[end_pos[0]][end_pos[1]]]
        if capture_moves:
            piece, start_pos, end_pos = random.choice(capture_moves)
        else:
            piece, start_pos, end_pos = random.choice(valid_moves)
        
        last_move_start = start_pos
        last_move_end = end_pos
        board[end_pos[0]][end_pos[1]] = piece
        board[start_pos[0]][start_pos[1]] = None
        piece.has_moved = True
        if piece.type == "pawn" and (end_pos[0] == 0 or end_pos[0] == 7):
            board[end_pos[0]][end_pos[1]] = ChessPiece(piece.color, "queen", PIECE_IMAGES[f"{piece.color}_queen"])

    if is_king_in_check(board, "white"):
        if is_checkmate(board, "white"):
            print("White is in checkmate. Game over!")
            pygame.quit()
            sys.exit()

    current_player = "white"

# Main game loop
def main():
    init_board()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(pygame.mouse.get_pos())
        draw_board()
        draw_pieces()
        pygame.display.flip()

        if current_player == "black":
            computer_move()

if __name__ == "__main__":
    main()