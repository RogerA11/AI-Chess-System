import gradio as gr
import chess
import gradio as gr
import chess
import chess.svg
import chess.engine
import time
import matplotlib.pyplot as plt
import numpy as np

class ChessApp:
    def __init__(self):
        self.board = chess.Board()
        self.engine_path = 'stockfish/stockfish-windows-x86-64-avx2.exe'  # Ensure this path is correct
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

    def draw_chessboard(self):
        svg = chess.svg.board(self.board)
        return f"<div style='width: 400px; height: 400px;'>{svg}</div>"

    def make_move(self, move):
        if move:
            try:
                # Player makes a move
                self.board.push_san(move)
                move_status = "Move successful"
            except ValueError:
                return self.draw_chessboard(), "Invalid move", None

        # After the player's move, check if the game is over
        if not self.board.is_game_over():
            # AI makes a move
            result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
            self.board.push(result.move)
            move_status += f", AI moved: {result.move}"

        graph = self.plot_sample_graph()  # Generate the graph after each move
        return self.draw_chessboard(), move_status, graph

    def plot_sample_graph(self):
        # Generate a simple line graph
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.figure(figsize=(5, 3))
        plt.plot(x, y)
        plt.title("Sample Sine Wave")
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.tight_layout()
        plt.close()
        return plt

    def undo_move(self):
        if len(self.board.move_stack) > 0:
            self.board.pop()  # Undo AI move
            if len(self.board.move_stack) > 0:
                self.board.pop()  # Undo player move
        return self.draw_chessboard(), "Move undone", None

    def reset_board(self):
        self.board.reset()
        return self.draw_chessboard(), "Board reset", None

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
