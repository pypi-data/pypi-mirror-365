import re
from typing import Any

from gyllm.envs.core import LLMEnv, Message, Request


class TftIpdEnv(LLMEnv):
    """Iterated Prisoner's Dilemma where the built‑in opponent plays tit‑for‑tat."""

    agents = ["player"]

    # Payoff matrix for (player_action, opponent_action)
    PAYOFFS: dict[tuple[str, str], tuple[int, int]] = {
        ("A", "A"): (3, 3),
        ("A", "B"): (0, 5),
        ("B", "A"): (5, 0),
        ("B", "B"): (1, 1),
    }

    def __init__(self, tokenize: callable, tokenize_kwargs: dict[str, Any]) -> None:
        super().__init__(tokenize, tokenize_kwargs)
        self.history: list[tuple[str, str]] = []
        self.messages: list[Message] = []
        self.player_score: int = 0
        self.opponent_score: int = 0
        self.system_prompt = (
            """You are participating in a repeated two-player game-theoretic scenario.\n"""
            "Each round you must choose action A or action B. The payoff matrix (your score shown first) is:\n\n"  # noqa: E501
            "                 Opponent\n"
            "               A          B\n"
            "  You A     (3, 3)     (0, 5)\n"
            "  You B     (5, 0)     (1, 1)\n\n"
            "Your objective is to maximise your cumulative score across rounds.\n"
            "Before selecting an action, reason step by step about the history of play so far to decide optimally.\n"
            "After that, put your decision in <action> </action> tags. In the action tags output **exactly** A or B, nothing else.\n"  # noqa: E501
            "You must finish your response with either <action>A</action> or <action>B</action>."
        )

        # self.system_prompt = (
        #     """You are participating in a repeated two-player game-theoretic scenario.\n"""
        #     "Each round you must choose action A or action B. The payoff matrix (your score shown first) is:\n\n"  # noqa: E501
        #     "                 Opponent\n"
        #     "               A          B\n"
        #     "  You A     (3, 3)     (0, 5)\n"
        #     "  You B     (5, 0)     (1, 1)\n\n"
        #     "Your objective is to maximise your cumulative score across rounds.\n"
        #     "Before selecting an action, reason step by step about the history of play so far to decide optimally.\n"
        #     "After that, finish your response with either 'ACTION: A' or 'ACTION: B'."
        # )

    def _parse_action(self, agent: str, completion: str) -> str:
        if agent == "player":
            # match = re.search(r"ACTION:\s*([AB])", completion, re.IGNORECASE)
            # if match:
            #     return match.group(1).strip().upper()
            match = re.search(r"<action>(.*)</action>", completion)
            if match:
                return match.group(1).strip()

        return "FAIL"

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    def _append(self, role: str, content: str) -> None:
        """Append a message to the running transcript."""
        self.messages.append({"role": role, "content": content})

    def _tit_for_tat(self) -> str:
        """Opponent strategy: cooperate on first move, then mimic player's previous move."""
        return "A" if len(self.history) == 0 else self.history[-1][0]

    # ------------------------------------------------------------------
    # Public API methods required by LLMEnv
    # ------------------------------------------------------------------
    def _initialize(self) -> list[Request]:
        """Reset the environment and produce the first request."""
        self.history.clear()
        self.player_score = 0
        self.opponent_score = 0
        self.messages = [
            Message(**{"role": "system", "content": self.system_prompt}),
            Message(**{
                "role": "environment",
                "content": "Starting round 1. You have 0 points. Your opponent has 0 points.",
            }),
        ]


        request = Request(**{
                "name": "player",
                "reward": 0.0,
                "messages": self.messages.copy(),
                "needs_action": True,
            })


        return [request]


    def _act(self, actions: dict[str, str]) -> list[Request]:
        """Advance one round given the agent's proposed action."""
        player_action = self._parse_action("player", actions["player"])
        assert player_action in {"A", "B"}, "Action must be 'A' or 'B'"

        # Opponent responds according to tit‑for‑tat
        opponent_action = self._tit_for_tat()

        # Determine payoffs
        player_reward, opponent_reward = self.PAYOFFS[(player_action, opponent_action)]
        self.player_score += player_reward
        self.opponent_score += opponent_reward

        # Log the round
        self.history.append((player_action, opponent_action))
        round_idx = len(self.history)  # 1‑based index

        self._append("player", actions["player"])
        self._append("opponent", f"<action>{opponent_action}</action>")
        self._append(
            "environment",
            (
                f"End of round {round_idx}. You played {player_action}, opponent played {opponent_action}. "
                f"Round payoff: {player_reward}. Total scores – You: {self.player_score}, "
                f"Opponent: {self.opponent_score}. Starting round {round_idx + 1}."
            ),
        )

        # Emit the next request for the agent
        return [
            Request(**{
                "name": "player",
                "reward": float(player_reward),
                "messages": self.messages.copy(),
                "needs_action": True,
            })
        ]

    # ------------------------------------------------------------------
    # Convenience methods (optional)
    # ------------------------------------------------------------------
    def render_history(self) -> list[Message]:
        """Return a copy of the current conversation log (for debugging/analysis)."""
        return self.messages.copy()
