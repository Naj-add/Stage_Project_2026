from asyncua import Server, ua

from .config import (
    OPCUA_ENDPOINT,
    OPCUA_NAMESPACE_URI
)


class OPCUAServerSimulator:

    def __init__(self):

        self.server = Server()

        self.server.set_endpoint(
            OPCUA_ENDPOINT
        )

        self.namespace_index = None

        self.objects_node = None

        self.sections = {}

        self.started = False

        self.initialized = False


    async def initialize(self):

        """
        Initialize the OPC-UA server address space
        and start the OPC-UA server.
        """

        if self.started:
            return

        # -------------------------------------------------
        # 1. Initialize the standard OPC-UA address space
        # -------------------------------------------------

        if not self.initialized:

            await self.server.init()

            self.initialized = True

            print(
                "OPC-UA address space initialized."
            )

        # -------------------------------------------------
        # 2. Register our custom namespace
        # -------------------------------------------------

        self.namespace_index = (
            await self.server.register_namespace(
                OPCUA_NAMESPACE_URI
            )
        )

        print(
            "OPC-UA namespace registered:"
        )

        print(
            f"{OPCUA_NAMESPACE_URI} "
            f"(index={self.namespace_index})"
        )

        # -------------------------------------------------
        # 3. Get the Objects folder
        # -------------------------------------------------

        self.objects_node = (
            self.server.get_objects_node()
        )

        # -------------------------------------------------
        # 4. Start the OPC-UA server
        # -------------------------------------------------

        await self.server.start()

        self.started = True

        print(
            "OPC-UA server started:"
        )

        print(
            OPCUA_ENDPOINT
        )


    async def add_section(
        self,
        section_code: str
    ):

        if section_code in self.sections:

            return self.sections[
                section_code
            ]

        if self.objects_node is None:

            raise RuntimeError(
                "OPC-UA server is not initialized."
            )

        # -------------------------------------------------
        # Section
        # -------------------------------------------------

        section_node = (
            await self.objects_node.add_object(
                self.namespace_index,
                f"Section_{section_code}"
            )
        )

        # -------------------------------------------------
        # Weight
        # -------------------------------------------------

        weight_node = (
            await section_node.add_variable(
                self.namespace_index,
                "Weight",
                0.0,
                ua.VariantType.Double
            )
        )

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        validation_node = (
            await section_node.add_variable(
                self.namespace_index,
                "Validation",
                False,
                ua.VariantType.Boolean
            )
        )

        # -------------------------------------------------
        # Cancellation
        # -------------------------------------------------

        cancellation_node = (
            await section_node.add_variable(
                self.namespace_index,
                "Cancellation",
                False,
                ua.VariantType.Boolean
            )
        )

        # -------------------------------------------------
        # PhotoRequested
        # -------------------------------------------------

        photo_node = (
            await section_node.add_variable(
                self.namespace_index,
                "PhotoRequested",
                False,
                ua.VariantType.Boolean
            )
        )

        # -------------------------------------------------
        # Make variables writable
        # -------------------------------------------------

        await weight_node.set_writable()

        await validation_node.set_writable()

        await cancellation_node.set_writable()

        await photo_node.set_writable()

        # -------------------------------------------------
        # Store nodes
        # -------------------------------------------------

        nodes = {

            "section": section_node,

            "weight": weight_node,

            "validation": validation_node,

            "cancellation": cancellation_node,

            "photo_requested": photo_node

        }

        self.sections[
            section_code
        ] = nodes

        print(
            f"OPC-UA section created: "
            f"Section_{section_code}"
        )

        return nodes


    async def write_weight(
        self,
        section_code: str,
        weight: float
    ):

        if section_code not in self.sections:

            raise ValueError(
                f"Unknown OPC-UA section: "
                f"{section_code}"
            )

        await self.sections[
            section_code
        ][
            "weight"
        ].write_value(
            float(weight)
        )


    async def write_validation(
        self,
        section_code: str,
        value: bool
    ):

        if section_code not in self.sections:

            raise ValueError(
                f"Unknown OPC-UA section: "
                f"{section_code}"
            )

        await self.sections[
            section_code
        ][
            "validation"
        ].write_value(
            bool(value)
        )


    async def write_cancellation(
        self,
        section_code: str,
        value: bool
    ):

        if section_code not in self.sections:

            raise ValueError(
                f"Unknown OPC-UA section: "
                f"{section_code}"
            )

        await self.sections[
            section_code
        ][
            "cancellation"
        ].write_value(
            bool(value)
        )


    async def write_photo_requested(
        self,
        section_code: str,
        value: bool
    ):

        if section_code not in self.sections:

            raise ValueError(
                f"Unknown OPC-UA section: "
                f"{section_code}"
            )

        await self.sections[
            section_code
        ][
            "photo_requested"
        ].write_value(
            bool(value)
        )


    async def stop(self):

        if self.started:

            await self.server.stop()

            self.started = False

            print(
                "OPC-UA server stopped."
            )