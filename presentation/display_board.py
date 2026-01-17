from __future__ import annotations

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

def rc_to_idx(row: int, col: int, cols: int = 10) -> int:
    col_in_row = (cols - 1 - col) if (row % 2 == 1) else col
    return row * cols + col_in_row


def idx_to_rc(idx: int, cols: int = 10) -> tuple[int, int]:
    row = idx // cols
    col_in_row = idx % cols
    col = (cols - 1 - col_in_row) if (row % 2 == 1) else col_in_row
    return row, col


class UiConfig:
    rows: int = 3
    cols: int = 10
    cell_size: int = 95
    margin: int = 30
    top_bar: int = 220

class DisplayBoard:
    def __init__(self, state: SenetState | None = None, config: UiConfig | None = None) -> None:
        self.config = config or UiConfig()
        self.state = state or create_initial_state()
        self.state.current_player = Player.BLACK

        self.rules = RulesAction()
        self.prob = Probability()
        self.result = Result()
        
        self.ai_depth = 3
        self.game_mode = "human_vs_human"
        self.ai_player = Player.WHITE
        self.controller = Expectiminimax(ui_callback=self._trigger_redraw, max_depth=self.ai_depth)

        self.current_roll: int | None = None
        self.ai_roll: int | None = None
        self.legal_moves: dict[int, int] = {}
        self.winner: Player | None = None
        self._needs_redraw = True
        self.ai_thinking = False
        self.depth = 6
        
        self.last_move_from: int | None = None
        self.last_move_to: int | None = None
        
        self.screen = None
        self.font = None
        self.big_font = None

        self._btn_toss: pygame.Rect | None = None
        self._btn_ai: pygame.Rect | None = None
        self._btn_skip: pygame.Rect | None = None
        self._sticks_rect: pygame.Rect | None = None
        self._btn_mode: pygame.Rect | None = None
        self._btn_depth_minus: pygame.Rect | None = None
        self._btn_depth_plus: pygame.Rect | None = None
        self._depth_display: pygame.Rect | None = None

    def _trigger_redraw(self) -> None:
        self._needs_redraw = True

    def _roll_and_compute_moves(self) -> None:
        self.current_roll = self.prob.throw_sticks()
        self.legal_moves = {}
        for move in self.rules.available_actions(self.state, self.current_roll):
            for from_idx, to_idx in move.items():
                self.legal_moves[int(from_idx)] = int(to_idx)
        
        self.last_move_from = None
        self.last_move_to = None

    def _mouse_to_index(self, mouse_pos: tuple[int, int]) -> int | None:
        mx, my = mouse_pos
        board_w = self.config.cols * self.config.cell_size
        screen_w = self.config.margin * 2 + board_w
        x0 = (screen_w - board_w) // 2
        y0 = self.config.margin + self.config.top_bar

        if mx < x0 or my < y0:
            return None

        col = (mx - x0) // self.config.cell_size
        row = (my - y0) // self.config.cell_size

        if col < 0 or col >= self.config.cols or row < 0 or row >= self.config.rows:
            return None

        return rc_to_idx(int(row), int(col), self.config.cols)

    def _handle_click(self, mouse_pos: tuple[int, int]) -> None:
        if self.winner is not None:
            return

        if self._btn_mode and self._btn_mode.collidepoint(mouse_pos):
            if self.game_mode == "human_vs_human":
                self.game_mode = "human_vs_expectiminimax"
            else:
                self.game_mode = "human_vs_human"
            return

        if self._btn_depth_minus and self._btn_depth_minus.collidepoint(mouse_pos):
            if self.ai_depth > 1:
                self.ai_depth -= 1
                self.controller.max_depth = self.ai_depth
            return

        if self._btn_depth_plus and self._btn_depth_plus.collidepoint(mouse_pos):
            if self.ai_depth < self.depth:
                self.ai_depth += 1
                self.controller.max_depth = self.ai_depth
            return

        if self._btn_toss and self._btn_toss.collidepoint(mouse_pos):
            if self.current_roll is None and not self.ai_thinking:
                    self._roll_and_compute_moves()
            return

        if self._btn_ai and self._btn_ai.collidepoint(mouse_pos):
            if self.current_roll is not None:
                self.state, best_action = self.controller.execute_turn(self.state, self.current_roll)
                if best_action:
                    self.last_move_from = best_action[0]
                    self.last_move_to = best_action[1]
                
                self.current_roll = None
                self.legal_moves = {}
                if self.state.is_terminal():
                    self.winner = self.state.get_winner()
            return

        if self._btn_skip and self._btn_skip.collidepoint(mouse_pos):
            self.current_roll = None
            self.ai_roll = None
            self.legal_moves = {}
            self.state.current_player = self.state.current_player.opponent()
            return

        idx = self._mouse_to_index(mouse_pos)
        if idx is None:
            return
        if self.current_roll is None:
            return
        if idx not in self.legal_moves:
            return

        from_idx = idx
        to_idx = self.legal_moves[idx]
        
        self.last_move_from = from_idx
        self.last_move_to = to_idx
        
        self.state = self.result.result(self.state, (from_idx, to_idx))
        self.current_roll = None
        self.legal_moves = {}

        if self.state.is_terminal():
            self.winner = self.state.get_winner()
            return
        
        if self.game_mode == "human_vs_expectiminimax" and self.state.current_player == self.ai_player:
            pygame.time.wait(300)
            
            self.ai_roll = self.prob.throw_sticks()
            if self.screen and self.font and self.big_font:
                self._draw(self.screen, self.font)
                pygame.display.flip()
            
            self.ai_thinking = True
            if self.screen and self.font and self.big_font:
                self._draw(self.screen, self.font)
                pygame.display.flip()
            
            self.state, best_action = self.controller.execute_turn(self.state, self.ai_roll)
            if best_action:
                self.last_move_from = best_action[0]
                self.last_move_to = best_action[1]
            
            self.ai_roll = None
            self.ai_thinking = False
            
            if self.state.is_terminal():
                self.winner = self.state.get_winner()

    def _draw_button(self, screen: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font) -> None:
        pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=1)
        pygame.draw.rect(screen, (170, 170, 170), rect, width=1, border_radius=1)
        label = font.render(text, True, (20, 20, 20))
        screen.blit(label, label.get_rect(center=rect.center))

    def _draw_sticks_area(self, screen: pygame.Surface, rect: pygame.Rect, roll_value: int | None) -> None:
        pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=12)
        pygame.draw.rect(screen, (120, 120, 120), rect, width=3, border_radius=12)

        roll_font = pygame.font.SysFont("arial", 42, bold=True)
        
        if roll_value is None:
            no_roll = roll_font.render("?", True, (180, 180, 180))
            screen.blit(no_roll, no_roll.get_rect(center=rect.center))
            return

        roll_text = roll_font.render(str(roll_value), True, (40, 40, 40))
        screen.blit(roll_text, roll_text.get_rect(center=rect.center))

    def _draw_special_icon(self, screen: pygame.Surface, rect: pygame.Rect, sq_num: int) -> None:
        cx, cy = rect.center
        color = (35, 35, 35)

        if sq_num == HOUSE_OF_REBIRTH:
            pygame.draw.circle(screen, color, (cx, cy - 14), 10, width=1)
            pygame.draw.line(screen, color, (cx, cy - 4), (cx, cy + 22), width=1)
            pygame.draw.line(screen, color, (cx - 12, cy + 6), (cx + 12, cy + 6), width=1)

        elif sq_num == HOUSE_OF_WATER:
            wave_width = rect.width - 20
            wave_start_x = rect.x + 10
            for k in range(4):
                y = rect.y + 20 + k * 12
                points = []
                num_waves = 3
                wave_segment = wave_width / (num_waves * 2)
                for i in range(num_waves * 2 + 1):
                    x = wave_start_x + i * wave_segment
                    y_offset = -6 if i % 2 == 1 else 0
                    points.append((x, y + y_offset))
                pygame.draw.lines(screen, color, False, points, 2)

        elif sq_num == HOUSE_OF_HAPPINESS:
            for j in range(3):
                x = rect.x + 26 + j * 18
                pygame.draw.line(screen, color, (x, rect.y + 18), (x, rect.y + rect.height - 18), 2)
                pygame.draw.circle(screen, color, (x, rect.y + rect.height - 18), self.depth, width=1)

        elif sq_num == HOUSE_OF_RE_ATOUM:
            pygame.draw.circle(screen, color, (cx - 14, cy - 6), 8, width=1)
            pygame.draw.circle(screen, color, (cx + 14, cy - 6), 8, width=1)
            pygame.draw.line(screen, color, (cx - 14, cy + 2), (cx - 14, cy + 26), 2)
            pygame.draw.line(screen, color, (cx + 14, cy + 2), (cx + 14, cy + 26), 2)

        elif sq_num == HOUSE_OF_HORUS:
            pygame.draw.circle(screen, color, (cx, cy), 26, width=3)
            pygame.draw.circle(screen, color, (cx, cy), 6)

        elif sq_num == HOUSE_OF_THREE_TRUTHS:
            for j in range(3):
                x = rect.x + 24 + j * 18
                pygame.draw.arc(screen, color, (x - 10, cy - 6, 20, 18), 0, 3.14, 2)

    def _draw(self, screen: pygame.Surface, big: pygame.font.Font) -> None:
        screen.fill((250, 248, 245))
        m = self.config.margin

        label_font = pygame.font.SysFont("arial", 22, bold=True)
        small = pygame.font.SysFont("arial", 16)

        board_w = self.config.cols * self.config.cell_size
        screen_w = screen.get_width()
        board_center_x = screen_w // 2

        black_box = pygame.Rect(m + 30, m + 15, 140, 55)
        white_box = pygame.Rect(screen_w - m - 170, m + 15, 140, 55)
        
        pygame.draw.rect(screen, (255, 255, 255), black_box, border_radius=10)
        pygame.draw.rect(screen, (80, 95, 110), black_box, width=3, border_radius=10)
        b_label = label_font.render(f"Black: {self.state.black_goal_count}", True, (20, 20, 20))
        screen.blit(b_label, (black_box.x + 12, black_box.y + 15))

        mode_text = "Human vs AI" if self.game_mode == "human_vs_expectiminimax" else "Human vs Human"
        self._btn_mode = pygame.Rect(m + 30, m + 80, 140, 35)
        
        mode_color = (150, 150, 150)
        pygame.draw.rect(screen, mode_color, self._btn_mode, border_radius=8)
        pygame.draw.rect(screen, (60, 60, 60), self._btn_mode, width=1, border_radius=8)
        mode_label = pygame.font.SysFont("arial", 16, bold=True).render(mode_text, True, (255, 255, 255))
        screen.blit(mode_label, mode_label.get_rect(center=self._btn_mode.center))

        if self.game_mode == "human_vs_expectiminimax":
            depth_y = m + 125
            depth_x = m + 30
            
            depth_label = pygame.font.SysFont("arial", 14).render("AI Depth:", True, (60, 60, 60))
            screen.blit(depth_label, (depth_x, depth_y))
            
            self._btn_depth_minus = pygame.Rect(depth_x, depth_y + 22, 35, 30)
            self._depth_display = pygame.Rect(depth_x + 40, depth_y + 22, 30, 30)
            self._btn_depth_plus = pygame.Rect(depth_x + 75, depth_y + 22, 35, 30)
            
            pygame.draw.rect(screen, (230, 230, 230), self._btn_depth_minus, border_radius=1)
            pygame.draw.rect(screen, (170, 170, 170), self._btn_depth_minus, width=1, border_radius=1)
            minus_label = label_font.render("-", True, (20, 20, 20))
            screen.blit(minus_label, minus_label.get_rect(center=self._btn_depth_minus.center))
            
            pygame.draw.rect(screen, (255, 255, 255), self._depth_display, border_radius=1)
            pygame.draw.rect(screen, (120, 120, 120), self._depth_display, width=1, border_radius=1)
            depth_num = label_font.render(str(self.ai_depth), True, (20, 20, 20))
            screen.blit(depth_num, depth_num.get_rect(center=self._depth_display.center))
            
            pygame.draw.rect(screen, (230, 230, 230), self._btn_depth_plus, border_radius=1)
            pygame.draw.rect(screen, (170, 170, 170), self._btn_depth_plus, width=1, border_radius=1)
            plus_label = label_font.render("+", True, (20, 20, 20))
            screen.blit(plus_label, plus_label.get_rect(center=self._btn_depth_plus.center))

        pygame.draw.rect(screen, (255, 255, 255), white_box, border_radius=10)
        pygame.draw.rect(screen, (120, 120, 120), white_box, width=3, border_radius=10)
        w_label = label_font.render(f"White: {self.state.white_goal_count}", True, (20, 20, 20))
        screen.blit(w_label, (white_box.x + 12, white_box.y + 15))

        sticks_w, sticks_h = 100, 80
        self._sticks_rect = pygame.Rect(0, 0, sticks_w, sticks_h)
        self._sticks_rect.centerx = white_box.centerx
        self._sticks_rect.top = white_box.bottom + 10
        
        if self.ai_thinking or self.ai_roll is not None:
            self._draw_sticks_area(screen, self._sticks_rect, self.ai_roll)
        else:
            self._draw_sticks_area(screen, self._sticks_rect, self.current_roll)

        title = big.render("Senet Game", True, (40, 40, 40))
        screen.blit(title, title.get_rect(center=(board_center_x, m + 42)))

        turn_color = (80, 95, 110) if self.state.current_player == Player.BLACK else (255, 255, 255)
        turn_bg = pygame.Rect(0, 0, 220, 42)
        turn_bg.center = (board_center_x, m + 95)
        pygame.draw.rect(screen, turn_color, turn_bg, border_radius=10)
        pygame.draw.rect(screen, (60, 60, 60), turn_bg, width=3, border_radius=10)
        turn_text_color = (255, 255, 255) if self.state.current_player == Player.BLACK else (20, 20, 20)
        
        if self.ai_thinking:
            turn_text = pygame.font.SysFont("arial", 20, bold=True).render("Thinking...", True, turn_text_color)
        elif self.game_mode == "human_vs_expectiminimax" and self.state.current_player == self.ai_player:
            turn_text = label_font.render(f"{self.state.current_player.name}'s Turn (AI)", True, turn_text_color)
        else:
            turn_text = label_font.render(f"{self.state.current_player.name}'s Turn", True, turn_text_color)
        screen.blit(turn_text, turn_text.get_rect(center=turn_bg.center))

        btn_w, btn_h = 110, 32
        self._btn_toss = pygame.Rect(board_center_x - 180, m + 145, btn_w, btn_h)
        self._btn_ai = pygame.Rect(board_center_x - 60, m + 145, btn_w, btn_h)
        self._btn_skip = pygame.Rect(board_center_x + 60, m + 145, btn_w, btn_h)

        self._draw_button(screen, self._btn_toss, "Throw Sticks", small)
        
        if self.current_roll is not None:
            self._draw_button(screen, self._btn_ai, "AI Move", small)
        else:
            pygame.draw.rect(screen, (200, 200, 200), self._btn_ai)
            pygame.draw.rect(screen, (150, 150, 150), self._btn_ai, width=2)
            label = small.render("AI Move", True, (140, 140, 140))
            screen.blit(label, label.get_rect(center=self._btn_ai.center))
        
        self._draw_button(screen, self._btn_skip, "Skip Turn", small)

        board_y = m + self.config.top_bar
        board_x = (screen_w - board_w) // 2
        board_h = self.config.rows * self.config.cell_size

        frame = pygame.Rect(board_x - 18, board_y - 18, board_w + 36, board_h + 36)
        pygame.draw.rect(screen, (120, 120, 120), frame, border_radius=18)

        light = (246, 247, 226)
        tan = (221, 186, 132)

        for row in range(self.config.rows):
            for col in range(self.config.cols):
                idx = rc_to_idx(row, col, self.config.cols)

                x = board_x + col * self.config.cell_size
                y = board_y + row * self.config.cell_size
                rect = pygame.Rect(x, y, self.config.cell_size - 10, self.config.cell_size - 10)
                rect.center = (x + self.config.cell_size // 2, y + self.config.cell_size // 2)

                bg = light if (row + col) % 2 == 0 else tan
                pygame.draw.rect(screen, bg, rect, border_radius=12)
                pygame.draw.rect(screen, (30, 30, 30), rect, width=1, border_radius=12)

                if idx in self.legal_moves:
                    pygame.draw.rect(screen, (40, 160, 90), rect, width=4, border_radius=12)
                
                if self.last_move_from is not None and idx == self.last_move_from:
                    pygame.draw.rect(screen, (60, 200, 110), rect, width=5, border_radius=12)
                
                if self.last_move_to is not None and idx == self.last_move_to:
                    pygame.draw.rect(screen, (60, 200, 110), rect, width=5, border_radius=12)

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
                if piece is None or piece == Player.EMPTY.value:
                    continue

                is_white = (piece == Player.WHITE.value)

                color = (255, 255, 255) if is_white else (80, 95, 110)
                center = rect.center
                radius = rect.width // 3
                pygame.draw.circle(screen, color, center, radius)
                pygame.draw.circle(screen, (30, 30, 30), center, radius, width=1)

        if self.winner is not None:
            win_bg = pygame.Rect(0, 0, 450, 70)
            win_bg.center = (board_center_x, board_y + board_h + 50)
            pygame.draw.rect(screen, (80, 180, 80), win_bg, border_radius=15)
            pygame.draw.rect(screen, (50, 120, 50), win_bg, width=4, border_radius=15)
            win = big.render(f"Winner: {self.winner.name}!", True, (255, 255, 255))
            screen.blit(win, win.get_rect(center=win_bg.center))
        else:
            hint_y = board_y + board_h + 40
            if self.current_roll is None:
                hint = small.render("Press 'Throw Sticks' or SPACE to roll the sticks", True, (80, 80, 80))
            else:
                hint = small.render(f"Roll: {self.current_roll} - Click a green highlighted piece to move", True, (30, 120, 60))
            hint_rect = hint.get_rect(center=(board_center_x, hint_y))
            screen.blit(hint, hint_rect)

    def run(self) -> None:
        pygame.init()
        try:
            board_w = self.config.cols * self.config.cell_size
            width = self.config.margin * 2 + board_w
            height = self.config.margin * 2 + self.config.top_bar + self.config.rows * self.config.cell_size + 80
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Senet Game")
            clock = pygame.time.Clock()

            self.font = pygame.font.SysFont("consolas", 22)
            self.big_font = pygame.font.SysFont("timesnewroman", 34, bold=True)

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        if event.key == pygame.K_SPACE:
                            if self.winner is None and self.current_roll is None and not self.ai_thinking:
                                if self.game_mode == "human_vs_expectiminimax" and self.state.current_player == self.ai_player:
                                    self.ai_roll = self.prob.throw_sticks()
                                    
                                    self.last_move_from = None
                                    self.last_move_to = None
                                    
                                    self._draw(self.screen, self.font)
                                    pygame.display.flip()
                                    
                                    self.ai_thinking = True
                                    self._draw(self.screen, self.font)
                                    pygame.display.flip()
                                    
                                    self.state, best_action = self.controller.execute_turn(self.state, self.ai_roll)
                                    if best_action:
                                        self.last_move_from = best_action[0]
                                        self.last_move_to = best_action[1]
                                    
                                    self.ai_roll = None
                                    self.ai_thinking = False
                                    
                                    if self.state.is_terminal():
                                        self.winner = self.state.get_winner()
                                else:
                                    self._roll_and_compute_moves()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._handle_click(event.pos)

                self._draw(self.screen, self.font)
                pygame.display.flip()
                clock.tick(60)
        finally:
            pygame.quit()


def run() -> None:
    DisplayBoard().run()
