from asyncua import Client

from .config import (
    OPCUA_ENDPOINT,
    OPCUA_NAMESPACE_URI
)


class OPCUAClient:

    def __init__(self):

        self.client = Client(
            url=OPCUA_ENDPOINT
        )

        self.namespace_index = None

        self.connected = False

    async def connect(self):

        await self.client.connect()

        self.namespace_index = (
            await self.client.get_namespace_index(
                OPCUA_NAMESPACE_URI
            )
        )

        self.connected = True

        print(
            "OPC-UA client connected."
        )

    async def disconnect(self):

        if self.connected:

            await self.client.disconnect()

            self.connected = False

    async def get_section_nodes(
        self,
        section_code: str
    ):

        objects = (
            self.client.get_objects_node()
        )

        section_node = await objects.get_child(
            [
                f"{self.namespace_index}:"
                f"Section_{section_code}"
            ]
        )

        children = (
            await section_node.get_children()
        )

        nodes = {}

        for child in children:

            browse_name = (
                await child.read_browse_name()
            )

            name = browse_name.Name

            if name == "Weight":
                nodes["weight"] = child

            elif name == "Validation":
                nodes["validation"] = child

            elif name == "Cancellation":
                nodes["cancellation"] = child

            elif name == "PhotoRequested":
                nodes[
                    "photo_requested"
                ] = child

        return nodes

    async def read_section(
        self,
        section_code: str
    ):

        nodes = await self.get_section_nodes(
            section_code
        )

        weight = await nodes[
            "weight"
        ].read_value()

        validation = await nodes[
            "validation"
        ].read_value()

        cancellation = await nodes[
            "cancellation"
        ].read_value()

        photo_requested = await nodes[
            "photo_requested"
        ].read_value()

        return {
            "weight": float(weight),
            "validation": bool(validation),
            "cancellation": bool(cancellation),
            "photo_requested": bool(
                photo_requested
            )
        }