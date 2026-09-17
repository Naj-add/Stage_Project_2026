import random

from .config import (
    ACTUAL_WEIGHT_MIN_RATIO,
    ACTUAL_WEIGHT_MAX_RATIO,
    CONVERGENCE_RATIO,
    INITIAL_NOISE_KG,
    FINAL_NOISE_KG,
    INITIAL_WEIGHT_RATIO
)


class WeightGenerator:

    def __init__(
        self,
        expected_weight: float
    ):

        self.expected_weight = expected_weight

        self.actual_target = (
            expected_weight
            * random.uniform(
                ACTUAL_WEIGHT_MIN_RATIO,
                ACTUAL_WEIGHT_MAX_RATIO
            )
        )

        self.current_weight = (
            expected_weight
            * INITIAL_WEIGHT_RATIO
        )

        self.step = 0

    def next_weight(self) -> float:

        self.step += 1

        difference = (
            self.actual_target
            - self.current_weight
        )

        convergence = (
            difference
            * CONVERGENCE_RATIO
        )

        noise_decay = max(
            FINAL_NOISE_KG,
            INITIAL_NOISE_KG
            / max(self.step, 1)
        )

        noise = random.uniform(
            -noise_decay,
            noise_decay
        )

        self.current_weight += (
            convergence
            + noise
        )

        return round(
            max(
                0,
                self.current_weight
            ),
            3
        )

    def get_target(self) -> float:
        return round(
            self.actual_target,
            3
        )