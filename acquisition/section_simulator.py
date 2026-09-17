import asyncio

from .models import SectionConfig
from .weight_generator import WeightGenerator


class SectionSimulator:

    def __init__(
        self,
        section: SectionConfig
    ):

        self.section = section

        self.weight_generator = (
            WeightGenerator(
                section.expected_weight
            )
        )

        self.weight = 0.0

        self.validation = False

        self.cancellation = False

        self.photo_requested = False

        self.running = False

    async def run(self):

        self.running = True

        while self.running:

            if not self.validation and not self.cancellation:

                self.weight = (
                    self.weight_generator.next_weight()
                )

            await asyncio.sleep(1)

    def stop(self):

        self.running = False

    def reset(self):

        self.weight = 0.0

        self.validation = False

        self.cancellation = False

        self.photo_requested = False

        self.weight_generator = (
            WeightGenerator(
                self.section.expected_weight
            )
        )