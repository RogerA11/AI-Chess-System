import gradio as gr
import chess
import chess.svg
import chess.engine
import numpy as np
import matplotlib.pyplot as plt

class ChessApp:
    def __init__(self):
        self.board = chess.Board()
        self.engine_path = 'stockfish/stockfish-windows-x86-64-avx2.exe'  # Make sure this path is correct
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.player_probabilities = []
        self.ai_probabilities = []

    def draw_chessboard(self):
        svg = chess.svg.board(self.board)
        return f"<div style='width: 400px; height: 400px;'>{svg}</div>"

    def eval_to_probability(self, pov_score):
        # First, check if the position is a checkmate.
        if pov_score.is_mate():
            # If a mate is found, return 100% probability for the player who has the mate.
            return (1.0, 0.0) if pov_score.mate() > 0 else (0.0, 1.0)

        # Now handle the normal cp() case:
        cp = pov_score.pov(self.board.turn).cp()
        if cp is None:
            # If cp is None, there's no clear advantage, treat the game as balanced.
            return (0.5, 0.5)

        # Calculate probability using the logistic function based on cp
        probability = 1 / (1 + np.exp(-0.004 * cp))
        # Return probabilities for both players, considering the turn.
        return (probability, 1 - probability) if self.board.turn == chess.WHITE else (1 - probability, probability)



    def get_evaluation(self):
        info = self.engine.analyse(self.board, chess.engine.Limit(depth=20))
        return info['score']

    def make_move(self, move):
        if move:
            try:
                self.board.push_san(move)
                move_status = "Player move successful"
            except ValueError:
                return self.draw_chessboard(), "Invalid move", None

        if not self.board.is_game_over():
            result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
            self.board.push(result.move)
            move_status += f", AI moved: {result.move}"

        eval = self.get_evaluation()
        player_prob, ai_prob = self.eval_to_probability(eval)
        self.player_probabilities.append(player_prob)
        self.ai_probabilities.append(ai_prob)
        
        graph = self.plot_probabilities()
        
        return self.draw_chessboard(), move_status, graph

    def plot_probabilities(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.player_probabilities, label='Player Win Probability')
        plt.plot(self.ai_probabilities, label='AI Win Probability')
        plt.title('Winning Probability Over Time')
        plt.xlabel('Move Number')
        plt.ylabel('Probability')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.close()  # Prevent it from displaying in another window
        return plt

    def undo_move(self):
        if len(self.board.move_stack) > 0:
            self.board.pop()  # Undo AI move
            self.board.pop()  # Undo player move
            self.player_probabilities.pop()
            self.ai_probabilities.pop()
        return self.draw_chessboard(), "Move undone", self.plot_probabilities()

    def reset_board(self):
        self.board.reset()
        self.player_probabilities.clear()
        self.ai_probabilities.clear()
        return self.draw_chessboard(), "Board reset", self.plot_probabilities()

app = ChessApp()

with gr.Blocks() as demo:
    with gr.Row():
        board_output = gr.HTML()
        status_output = gr.Text()
        graph_output = gr.Plot()

    with gr.Row():
        move_input = gr.Textbox(label="Enter your move (e.g., e2e4)", placeholder="Move in SAN format", lines=1)
        submit_button = gr.Button("Submit Move")
        undo_button = gr.Button("Undo Move")
        reset_button = gr.Button("Reset Board")

    submit_button.click(app.make_move, inputs=move_input, outputs=[board_output, status_output, graph_output])
    undo_button.click(app.undo_move, inputs=[], outputs=[board_output, status_output, graph_output])
    reset_button.click(app.reset_board, inputs=[], outputs=[board_output, status_output, graph_output])

demo.launch()
