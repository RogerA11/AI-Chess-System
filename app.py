import gradio as gr
import chess
import chess.svg
import chess.engine
import time

class ChessApp:
    def __init__(self):
        self.board = chess.Board()
        self.engine_path = 'stockfish/stockfish-windows-x86-64-avx2.exe'  # Ensure this path is correct
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.move_history = []
        self.game_start_time = time.time()

    def draw_chessboard(self):
        svg = chess.svg.board(board=self.board)
        return f"<div style='width: 400px; height: 400px;'>{svg}</div>"

    def make_move(self, move):
        if not move:
            return self.draw_chessboard(), "Awaiting move...", self.move_history, self.get_game_timer()
        if self.engine is None:
            return self.draw_chessboard(), "Chess engine not initialized. Please check the engine path.", self.move_history, self.get_game_timer()
        try:
            self.board.push_san(move)
            self.move_history.append(move)
            result = self.draw_chessboard()
            status = "Move accepted: " + move
            if not self.board.is_game_over():
                result, status = self.ai_move()
            return result, status, self.move_history, self.get_game_timer()
        except ValueError:
            return self.draw_chessboard(), "Invalid move: " + move, self.move_history, self.get_game_timer()

    # Other methods remain the same...

app = ChessApp()

def move(move):
    return app.make_move(move)

def undo():
    return app.undo_move()

def reset():
    return app.reset_game()

iface = gr.Interface(
    fn=move,
    inputs=[gr.Textbox(label="Move")],
    outputs=[gr.HTML(), gr.Text(label="Move Status"), gr.Dataframe(label="Move History"), gr.Text(label="Game Timer")],
    title="AI Chess Game",
    description="Play chess against an AI. Enter your moves in standard chess notation."
)

iface.add_event("click", undo, "Undo Move", inputs=None, outputs=iface.outputs)
iface.add_event("click", reset, "Reset Game", inputs=None, outputs=iface.outputs)

if __name__ == "__main__":
    iface.launch()
