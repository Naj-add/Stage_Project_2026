import asyncio
from datetime import datetime
from threading import Lock

from .config import (
    READ_INTERVAL_SECONDS,
    WEIGHT_SOURCE
)

from .models import (
    OperationRuntime,
    SectionConfig,
    WeighingRuntime
)

from .opcua_server import (
    OPCUAServerSimulator
)

from .opcua_client import (
    OPCUAClient
)

from .section_simulator import (
    SectionSimulator
)

from .state_machine import (
    WeighingStateMachine,
    InvalidTransition
)


class AcquisitionService:

    def __init__(self):

        self.opcua_server = (
            OPCUAServerSimulator()
        )

        self.opcua_client = OPCUAClient()

        self.state_machine = (
            WeighingStateMachine()
        )

        self.operations = {}

        self.simulators = {}

        self.running = False

        self.lock = Lock()

    async def initialize(self):

       await self.opcua_server.initialize()

       await self.opcua_client.connect()

       print("Acquisition service initialized.")

    async def configure_operation(
        self,
        operation_id: int,
        sections: list[dict]
    ):

        with self.lock:

            if operation_id in self.operations:

                return self.operations[
                    operation_id
                ]

            operation = OperationRuntime(
                operation_id=operation_id
            )

            for section_data in sections:

                section = SectionConfig(
                    section_id=int(
                        section_data[
                            "section_id"
                        ]
                    ),
                    code=str(
                        section_data["code"]
                    ),
                    expected_weight=float(
                        section_data[
                            "expected_weight"
                        ]
                    )
                )

                weighing = WeighingRuntime(
                    operation_id=operation_id,
                    section_id=section.section_id,
                    section_code=section.code,
                    expected_weight=section.expected_weight,
                    source_s7=WEIGHT_SOURCE
                )

                operation.sections[
                    section.code
                ] = weighing

            self.operations[
                operation_id
            ] = operation

        # Create OPC-UA nodes dynamically
        for section_code in operation.sections:

            await self.opcua_server.add_section(
                section_code
            )

        return operation

    async def start_operation(
        self,
        operation_id: int,
        section_code: str | None = None
    ):
        operation = self.operations.get(operation_id)

        if operation is None:
            raise ValueError("Operation not configured.")

        if not operation.sections:
            raise ValueError("Operation has no sections.")

        if section_code is None:
            section_code = next(iter(operation.sections))

        if section_code not in operation.sections:
            raise ValueError(f"Unknown section: {section_code}")

        weighing = operation.sections[section_code]

        # ---------------------------------------------------------
        # RESUME / IDEMPOTENT BEHAVIOR
        # ---------------------------------------------------------

        # Already weighing:
        # Do NOT create a second simulator.
        if weighing.state == self.state_machine.WEIGHING:
            operation.active_section_code = section_code
            operation.status = "IN_PROGRESS"

            simulator_key = f"{operation_id}:{section_code}"

            if simulator_key not in self.simulators:
                simulator = SectionSimulator(
                    SectionConfig(
                        section_id=weighing.section_id,
                        code=section_code,
                        expected_weight=weighing.expected_weight
                    )
                )

                self.simulators[simulator_key] = simulator

                asyncio.create_task(simulator.run())
                asyncio.create_task(
                    self.monitor_section(
                        operation_id,
                        section_code
                    )
                )

            return weighing

        # Already ready:
        # Do not restart the weighing.
        if weighing.state == self.state_machine.READY:
            operation.active_section_code = section_code
            operation.status = "IN_PROGRESS"
            return weighing

        # Already validated/completed/cancelled:
        if weighing.state in (
            self.state_machine.VALIDATED,
            self.state_machine.PHOTO_REQUESTED,
            self.state_machine.COMPLETED,
            self.state_machine.CANCELLED
        ):
            return weighing

        # ---------------------------------------------------------
        # NORMAL START
        # ---------------------------------------------------------

        if weighing.state != self.state_machine.IDLE:
            raise ValueError(
                f"Cannot start weighing from state {weighing.state}."
            )

        self.state_machine.start(weighing)

        operation.active_section_code = section_code
        operation.status = "IN_PROGRESS"

        simulator_key = f"{operation_id}:{section_code}"

        simulator = SectionSimulator(
            SectionConfig(
                section_id=weighing.section_id,
                code=section_code,
                expected_weight=weighing.expected_weight
            )
        )

        self.simulators[simulator_key] = simulator

        asyncio.create_task(simulator.run())

        asyncio.create_task(
            self.monitor_section(
                operation_id,
                section_code
            )
        )

        return weighing

    async def monitor_section(
        self,
        operation_id: int,
        section_code: str
    ):

        simulator_key = (
            f"{operation_id}:"
            f"{section_code}"
        )

        simulator = self.simulators[
            simulator_key
        ]

        weighing = self.operations[
            operation_id
        ].sections[
            section_code
        ]

        while weighing.state == "WEIGHING":

            # Generate next simulated PLC value
            await asyncio.sleep(
                READ_INTERVAL_SECONDS
            )

            # Write simulated PLC value
            await self.opcua_server.write_weight(
                section_code,
                simulator.weight
            )

            # Read it through OPC-UA client
            plc_data = (
                await self.opcua_client.read_section(
                    section_code
                )
            )

            self.state_machine.update_weight(
                weighing,
                plc_data["weight"]
            )

            if weighing.state == "READY":

                print(
                    f"[READY] "
                    f"Operation {operation_id} "
                    f"| Section {section_code} "
                    f"| Weight "
                    f"{weighing.current_weight} kg"
                )

                break

            if plc_data["cancellation"]:

                self.state_machine.cancel(
                    weighing
                )

                break

        simulator.stop()

    async def validate(
        self,
        operation_id: int,
        section_code: str,
        user_id: int
    ):

        operation = self.operations.get(
            operation_id
        )

        if operation is None:

            raise ValueError(
                "Operation not found."
            )

        weighing = operation.sections.get(
            section_code
        )

        if weighing is None:

            raise ValueError(
                "Section not found."
            )

        self.state_machine.validate(
            weighing,
            user_id
        )

        await self.opcua_server.write_validation(
            section_code,
            True
        )

        return weighing

    async def cancel(
        self,
        operation_id: int,
        section_code: str
    ):

        operation = self.operations.get(
            operation_id
        )

        if operation is None:

            raise ValueError(
                "Operation not found."
            )

        weighing = operation.sections.get(
            section_code
        )

        if weighing is None:

            raise ValueError(
                "Section not found."
            )

        self.state_machine.cancel(
            weighing
        )

        await self.opcua_server.write_cancellation(
            section_code,
            True
        )

        simulator_key = (
            f"{operation_id}:"
            f"{section_code}"
        )

        simulator = self.simulators.get(
            simulator_key
        )

        if simulator:

            simulator.stop()

        return weighing

    def get_operation(
        self,
        operation_id: int
    ):

        return self.operations.get(
            operation_id
        )

    def get_section(
        self,
        operation_id: int,
        section_code: str
    ):

        operation = self.operations.get(
            operation_id
        )

        if not operation:
            return None

        return operation.sections.get(
            section_code
        )

    def get_all_operations(self):

        return list(
            self.operations.values()
        )