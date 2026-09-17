from datetime import datetime

from .config import (
    STABILITY_REQUIRED_READINGS,
    STABILITY_TOLERANCE_KG
)


class InvalidTransition(Exception):
    pass


class WeighingStateMachine:

    IDLE = "IDLE"
    WEIGHING = "WEIGHING"
    READY = "READY"
    VALIDATED = "VALIDATED"
    PHOTO_REQUESTED = "PHOTO_REQUESTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    def start(self, weighing):

        if weighing.state != self.IDLE:
            raise InvalidTransition(
                f"Cannot start from state "
                f"{weighing.state}"
            )

        weighing.state = self.WEIGHING
        weighing.started_at = datetime.now()
        weighing.last_update = datetime.now()

    def update_weight(
        self,
        weighing,
        weight: float
    ):

        if weighing.state != self.WEIGHING:
            return

        previous_weight = weighing.current_weight

        weighing.current_weight = weight

        weighing.history.append(weight)

        if previous_weight > 0:

            difference = abs(
                weight - previous_weight
            )

            if difference <= STABILITY_TOLERANCE_KG:

                weighing.stable_readings += 1

            else:

                weighing.stable_readings = 0

        else:

            weighing.stable_readings = 0

        weighing.is_stable = (
            weighing.stable_readings
            >= STABILITY_REQUIRED_READINGS
        )

        if weighing.is_stable:

            weighing.state = self.READY

            weighing.ready_at = datetime.now()

        weighing.last_update = datetime.now()

    def validate(
        self,
        weighing,
        user_id: int
    ):

        if weighing.state != self.READY:
            raise InvalidTransition(
                "Weighing is not ready for validation."
            )

        weighing.state = self.VALIDATED

        weighing.validated_at = datetime.now()

        weighing.validated_by = user_id

        weighing.last_update = datetime.now()

    def request_photo(self, weighing):

        if weighing.state != self.VALIDATED:
            raise InvalidTransition(
                "Photo can only be requested "
                "after validation."
            )

        weighing.state = self.PHOTO_REQUESTED

        weighing.last_update = datetime.now()

    def complete(self, weighing):

        if weighing.state != self.PHOTO_REQUESTED:
            raise InvalidTransition(
                "Weighing must request photo "
                "before completion."
            )

        weighing.state = self.COMPLETED

        weighing.last_update = datetime.now()

    def cancel(self, weighing):

        if weighing.state not in (
            self.WEIGHING,
            self.READY
        ):
            raise InvalidTransition(
                f"Cannot cancel from state "
                f"{weighing.state}"
            )

        weighing.state = self.CANCELLED

        weighing.cancelled_at = datetime.now()

        weighing.last_update = datetime.now()