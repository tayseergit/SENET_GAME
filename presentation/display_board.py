from __future__ import annotations

from dataclasses import dataclass

import pygame

from core.actions import Action as RulesAction
from core.controller.probability import Probability
from core.results import Result
from core.states import SenetState, create_initial_state
from core.component.player import Player


@dataclass
class UiConfig:
    rows: int = 3
    cols: int = 10
    cell_size: int = 80
    margin: int = 20
    top_bar: int = 90


class DisplayBoard:
    def __init__(self, state: SenetState | None = None, config: UiConfig | None = None) -> None:
        self.config = config or UiConfig()
        self.state = state or create_initial_state(rows=self.config.rows, cols=self.config.cols)
        self.state.current_player = Player.BLACK
        self.rules = RulesAction()
        self.prob = Probability()
        self.result = Result()

        self.current_roll: int | None = None
        self.legal_moves: dict[int, int] = {}
        self.winner: Player | None = None

    def run(self) -> None:
        pygame.init()
        try:
            width = self.config.margin * 2 + self.config.cols * self.config.cell_size
            height = self.config.margin * 2 + self.config.top_bar + self.config.rows * self.config.cell_size
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("SENET")
            clock = pygame.time.Clock()
            font = pygame.font.SysFont("consolas", 24)

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        if event.key == pygame.K_SPACE:
                            if self.winner is None:
                                self._roll_and_compute_moves()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.winner is None:
                            self._handle_click(event.pos)

                self._draw(screen, font)
                pygame.display.flip()
                clock.tick(60)
        finally:
            pygame.quit()

    def _roll_and_compute_moves(self) -> None:
        self.current_roll = self.prob.throw_sticks()
        self.legal_moves = {}
        for move in self.rules.available_actions(self.state, self.current_roll):
            for from_idx, to_idx in move.items():
                self.legal_moves[int(from_idx)] = int(to_idx)

    def _handle_click(self, mouse_pos: tuple[int, int]) -> None:
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

        if self.state.white_number == 0:
            self.winner = Player.BLACK
        elif self.state.black_number == 0:
            self.winner = Player.WHITE

    def _mouse_to_index(self, mouse_pos: tuple[int, int]) -> int | None:
        mx, my = mouse_pos
        x0 = self.config.margin
        y0 = self.config.margin + self.config.top_bar

        if mx < x0 or my < y0:
            return None

        col = (mx - x0) // self.config.cell_size
        row = (my - y0) // self.config.cell_size

        if col < 0 or col >= self.config.cols or row < 0 or row >= self.config.rows:
            return None

        return int(row * self.config.cols + col)

    def _draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        screen.fill((15, 15, 18))

        if self.winner is not None:
            title = f"Winner: {self.winner.value} (ESC to exit)"
        else:
            title = "Press SPACE to roll" if self.current_roll is None else f"Roll: {self.current_roll}"
        info = f"Turn: {self.state.current_player.value}"
        t_surf = font.render(title, True, (240, 240, 240))
        i_surf = font.render(info, True, (240, 240, 240))
        screen.blit(t_surf, (self.config.margin, self.config.margin))
        screen.blit(i_surf, (self.config.margin, self.config.margin + 32))

        counts = f"W:{self.state.white_number}  B:{self.state.black_number}"
        c_surf = font.render(counts, True, (200, 200, 200))
        screen.blit(c_surf, (self.config.margin, self.config.margin + 64))

        for row in range(self.config.rows):
            for col in range(self.config.cols):
                idx = row * self.config.cols + col
                x = self.config.margin + col * self.config.cell_size
                y = self.config.margin + self.config.top_bar + row * self.config.cell_size
                rect = pygame.Rect(x, y, self.config.cell_size, self.config.cell_size)

                bg = (40, 40, 48)
                if idx in self.legal_moves:
                    bg = (30, 120, 70)
                pygame.draw.rect(screen, bg, rect, border_radius=10)
                pygame.draw.rect(screen, (85, 85, 95), rect, width=2, border_radius=10)

                piece = self.state.board[idx]
                if piece is not None:
                    # Support both Player enum and plain string values
                    val = piece.value if hasattr(piece, "value") else str(piece)
                    is_white = val == "W"
                    color = (240, 240, 240) if is_white else (30, 30, 30)
                    center = (x + self.config.cell_size // 2, y + self.config.cell_size // 2)
                    pygame.draw.circle(screen, color, center, self.config.cell_size // 3)
                    pygame.draw.circle(screen, (200, 180, 120), center, self.config.cell_size // 3, width=2)

                    label_color = (60, 140, 255) if is_white else (220, 60, 60)
                    label = font.render(val, True, label_color)
                    label_rect = label.get_rect(center=center)
                    screen.blit(label, label_rect)


def run() -> None:
    DisplayBoard().run()
