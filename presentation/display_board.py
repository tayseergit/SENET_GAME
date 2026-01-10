from __future__ import annotations

from dataclasses import dataclass
import pygame

from core.actions import Action as RulesAction
from core.controller.probability import Probability
from core.controller.expectiminimax import Expectiminimax
from core.results import Result
from core.states import SenetState, create_initial_state
from core.component.player import Player
from core.component.main_house import (
    HOUSE_OF_REBIRTH,
    HOUSE_OF_HAPPINESS,
    HOUSE_OF_WATER,
    HOUSE_OF_THREE_TRUTHS,
    HOUSE_OF_RE_ATOUM,
    HOUSE_OF_HORUS,
)

# =========================
# ✅ Senet "snake" mapping (display only)
# Row0: 1 -> 10
# Row1: 20 <- 11
# Row2: 21 -> 30
# board stays 1D: indices 0..29 (square = idx+1)
# =========================
def rc_to_idx(row: int, col: int, cols: int = 10) -> int:
    """Screen (row,col) -> 1D board index (0..29) with snake mapping."""
    col_in_row = (cols - 1 - col) if (row % 2 == 1) else col
    return row * cols + col_in_row


def idx_to_rc(idx: int, cols: int = 10) -> tuple[int, int]:
    """1D board index (0..29) -> Screen (row,col) with snake mapping."""
    row = idx // cols
    col_in_row = idx % cols
    col = (cols - 1 - col_in_row) if (row % 2 == 1) else col_in_row
    return row, col


@dataclass
class UiConfig:
    rows: int = 3
    cols: int = 10
    cell_size: int = 95
    margin: int = 30
    top_bar: int = 220  # مساحة الأعلى مثل الصورة


class DisplayBoard:
    def __init__(self, state: SenetState | None = None, config: UiConfig | None = None) -> None:
        self.config = config or UiConfig()
        self.state = state or create_initial_state()
        self.state.current_player = Player.BLACK

        self.rules = RulesAction()
        self.prob = Probability()
        self.result = Result()
        self.controller = Expectiminimax(ui_callback=self._trigger_redraw)

        self.current_roll: int | None = None
        self.legal_moves: dict[int, int] = {}
        self.winner: Player | None = None
        self._needs_redraw = True

        self._btn_toss: pygame.Rect | None = None
        self._btn_ai: pygame.Rect | None = None
        self._btn_skip: pygame.Rect | None = None
        self._sticks_rect: pygame.Rect | None = None

    def _trigger_redraw(self) -> None:
        self._needs_redraw = True

    # =========================
    # Helpers for moves
    # =========================
    def _roll_and_compute_moves(self) -> None:
        self.current_roll = self.prob.throw_sticks()
        self.legal_moves = {}
        for move in self.rules.available_actions(self.state, self.current_roll):
            for from_idx, to_idx in move.items():
                self.legal_moves[int(from_idx)] = int(to_idx)

    def _mouse_to_index(self, mouse_pos: tuple[int, int]) -> int | None:
        """✅ Convert mouse click to 1D board index using snake mapping."""
        mx, my = mouse_pos
        x0 = self.config.margin
        y0 = self.config.margin + self.config.top_bar

        if mx < x0 or my < y0:
            return None

        col = (mx - x0) // self.config.cell_size
        row = (my - y0) // self.config.cell_size

        if col < 0 or col >= self.config.cols or row < 0 or row >= self.config.rows:
            return None

        # ✅ snake mapping (screen -> 1D)
        return rc_to_idx(int(row), int(col), self.config.cols)

    def _handle_click(self, mouse_pos: tuple[int, int]) -> None:
        if self.winner is not None:
            return

        # 1) Buttons
        if self._btn_toss and self._btn_toss.collidepoint(mouse_pos):
            if self.current_roll is None:
                self._roll_and_compute_moves()
            return

        if self._btn_ai and self._btn_ai.collidepoint(mouse_pos):
            self.state = self.controller.execute_turn(self.state)
            self.current_roll = None
            self.legal_moves = {}
            if self.state.is_terminal():
                self.winner = self.state.get_winner()
            return

        if self._btn_skip and self._btn_skip.collidepoint(mouse_pos):
            self.current_roll = None
            self.legal_moves = {}
            self.state.current_player = self.state.current_player.opponent
            return

        # 2) board click (move)
        idx = self._mouse_to_index(mouse_pos)
        if idx is None:
            return
        if self.current_roll is None:
            return
        if idx not in self.legal_moves:
            return

        from_idx = idx
        to_idx = self.legal_moves[idx]
        self.state = self.result.result(self.state, (from_idx, to_idx), int(self.current_roll))
        self.current_roll = None
        self.legal_moves = {}

        if self.state.is_terminal():
            self.winner = self.state.get_winner()

    # =========================
    # Drawing helpers (style)
    # =========================
    def _draw_button(self, screen: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font) -> None:
        pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=6)
        pygame.draw.rect(screen, (170, 170, 170), rect, width=2, border_radius=6)
        label = font.render(text, True, (20, 20, 20))
        screen.blit(label, label.get_rect(center=rect.center))

    def _draw_sticks_area(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(screen, (230, 245, 230), rect, border_radius=16)
        pygame.draw.rect(screen, (140, 230, 140), rect, width=4, border_radius=16)

        inner = rect.inflate(-28, -28)
        stick_w = inner.width // 6
        gap = stick_w // 2
        x = inner.x + gap
        for _ in range(5):
            r = pygame.Rect(x, inner.y, stick_w, inner.height)
            pygame.draw.rect(screen, (250, 245, 235), r, border_radius=8)
            x += stick_w + gap

    def _draw_special_icon(self, screen: pygame.Surface, rect: pygame.Rect, sq_num: int) -> None:
        cx, cy = rect.center
        color = (35, 35, 35)

        if sq_num == (HOUSE_OF_REBIRTH):
            pygame.draw.circle(screen, color, (cx, cy - 14), 10, width=2)
            pygame.draw.line(screen, color, (cx, cy - 4), (cx, cy + 22), width=2)
            pygame.draw.line(screen, color, (cx - 12, cy + 6), (cx + 12, cy + 6), width=2)

        elif sq_num == HOUSE_OF_WATER:
            for k in range(4):
                y = rect.y + 18 + k * 10
                pygame.draw.lines(
                    screen, color, False,
                    [(rect.x + 14, y), (rect.x + 26, y - 6), (rect.x + 38, y),
                     (rect.x + 50, y - 6), (rect.x + 62, y), (rect.x + 74, y - 6),
                     (rect.x + 86, y)],
                    2
                )

        elif sq_num == HOUSE_OF_HAPPINESS:
            for j in range(3):
                x = rect.x + 26 + j * 18
                pygame.draw.line(screen, color, (x, rect.y + 18), (x, rect.y + rect.height - 18), 2)
                pygame.draw.circle(screen, color, (x, rect.y + rect.height - 18), 6, width=2)

        elif sq_num == HOUSE_OF_RE_ATOUM:
            pygame.draw.circle(screen, color, (cx - 14, cy - 6), 8, width=2)
            pygame.draw.circle(screen, color, (cx + 14, cy - 6), 8, width=2)
            pygame.draw.line(screen, color, (cx - 14, cy + 2), (cx - 14, cy + 26), 2)
            pygame.draw.line(screen, color, (cx + 14, cy + 2), (cx + 14, cy + 26), 2)

        elif sq_num == HOUSE_OF_HORUS:
            pygame.draw.circle(screen, color, (cx, cy), 26, width=4)
            pygame.draw.circle(screen, color, (cx, cy), 8)

        elif sq_num == HOUSE_OF_THREE_TRUTHS:
            for j in range(3):
                x = rect.x + 24 + j * 18
                pygame.draw.arc(screen, color, (x - 10, cy - 6, 20, 18), 0, 3.14, 2)

    # =========================
    # Main draw (like image) + ✅ correct snake display
    # =========================
    def _draw(self, screen: pygame.Surface, font: pygame.font.Font, big: pygame.font.Font) -> None:
        screen.fill((255, 255, 255))
        m = self.config.margin

        label_font = pygame.font.SysFont("timesnewroman", 26, bold=True)
        small = pygame.font.SysFont("consolas", 18)

        # score boxes (you can replace 0 with your own scoring if needed)
        b_label = label_font.render("Black: 0", True, (0, 0, 0))
        screen.blit(b_label, (m + 80, m + 8))
      
        w_label = label_font.render("White: 0", True, (0, 0, 0))
        screen.blit(w_label, (m + 320, m + 8))
       
        # title + turn
        title = big.render("Senet", True, (0, 0, 0))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, m + 18)))

        turn_text = big.render(f"{self.state.current_player.value}'s turn", True, (0, 0, 0))
        screen.blit(turn_text, turn_text.get_rect(center=(screen.get_width() // 2, m + 70)))

        # buttons
        btn_w, btn_h = 85, 26
        cx = screen.get_width() // 2
        self._btn_toss = pygame.Rect(cx - 90, m + 105, btn_w, btn_h)
        self._btn_ai = pygame.Rect(cx + 5, m + 105, btn_w, btn_h)
        self._btn_skip = pygame.Rect(cx + 5, m + 135, btn_w, btn_h)

        self._draw_button(screen, self._btn_toss, "Toss!", small)
        self._draw_button(screen, self._btn_ai, "Ask the AI!", small)
        self._draw_button(screen, pygame.Rect(cx - 90, m + 135, btn_w, btn_h), "Select a piece", small)
        self._draw_button(screen, self._btn_skip, "Skip turn", small)

        # board frame
        board_x = m
        board_y = m + self.config.top_bar
        board_w = self.config.cols * self.config.cell_size
        board_h = self.config.rows * self.config.cell_size

        frame = pygame.Rect(board_x - 18, board_y - 18, board_w + 36, board_h + 36)
        pygame.draw.rect(screen, (120, 120, 120), frame, border_radius=18)

        light = (246, 247, 226)
        tan = (221, 186, 132)

        # ✅ DISPLAY LOOP: iterate screen cells (row,col) but fetch board using snake idx
        for row in range(self.config.rows):
            for col in range(self.config.cols):
                idx = rc_to_idx(row, col, self.config.cols)  # ✅ snake mapping

                x = board_x + col * self.config.cell_size
                y = board_y + row * self.config.cell_size
                rect = pygame.Rect(x, y, self.config.cell_size - 10, self.config.cell_size - 10)
                rect.center = (x + self.config.cell_size // 2, y + self.config.cell_size // 2)

                bg = light if (row + col) % 2 == 0 else tan
                pygame.draw.rect(screen, bg, rect, border_radius=12)
                pygame.draw.rect(screen, (30, 30, 30), rect, width=2, border_radius=12)

                # highlight legal FROM squares (keys are 1D idx)
                if idx in self.legal_moves:
                    pygame.draw.rect(screen, (40, 160, 90), rect, width=4, border_radius=12)

                # special squares based on real square number (idx+1)
                sq_num = idx 
                if sq_num in {
                    HOUSE_OF_REBIRTH,
                    HOUSE_OF_HAPPINESS,
                    HOUSE_OF_WATER,
                    HOUSE_OF_THREE_TRUTHS,
                    HOUSE_OF_RE_ATOUM,
                    HOUSE_OF_HORUS,
                }:
                    self._draw_special_icon(screen, rect, sq_num)

                piece = self.state.board[idx]
                if piece is None or piece == Player.EMPTY:
                    continue

                val = piece.value if hasattr(piece, "value") else str(piece)
                is_white = (val == "W")

                color = (250, 250, 250) if is_white else (110, 130, 150)
                center = rect.center
                radius = rect.width // 3
                pygame.draw.circle(screen, color, center, radius)
                pygame.draw.circle(screen, (40, 40, 40), center, radius, width=2)

        # roll info
        if self.winner is not None:
            win = big.render(f"Winner: {self.winner.value}", True, (0, 0, 0))
            screen.blit(win, (m, m + 150))
        else:
            if self.current_roll is None:
                hint = small.render("Click Toss! (or SPACE) to roll", True, (40, 40, 40))
            else:
                hint = small.render(f"Roll: {self.current_roll}  (click a highlighted piece)", True, (40, 40, 40))
            screen.blit(hint, (m, m + 150))

    # =========================
    # Main loop
    # =========================
    def run(self) -> None:
        pygame.init()
        try:
            width = self.config.margin * 2 + self.config.cols * self.config.cell_size + 350
            height = self.config.margin * 2 + self.config.top_bar + self.config.rows * self.config.cell_size + 20
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Senet")
            clock = pygame.time.Clock()

            font = pygame.font.SysFont("consolas", 22)
            big = pygame.font.SysFont("timesnewroman", 34, bold=True)

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        if event.key == pygame.K_SPACE:
                            if self.winner is None and self.current_roll is None:
                                self._roll_and_compute_moves()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._handle_click(event.pos)

                self._draw(screen, font, big)
                pygame.display.flip()
                clock.tick(60)
        finally:
            pygame.quit()


def run() -> None:
    DisplayBoard().run()
