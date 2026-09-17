import os


# ============================================================
# OPC-UA
# ============================================================

OPCUA_ENDPOINT = os.getenv(
    "OPCUA_ENDPOINT",
    "opc.tcp://127.0.0.1:4840/zeta-mesure/"
)

OPCUA_NAMESPACE_URI = os.getenv(
    "OPCUA_NAMESPACE_URI",
    "http://zeta-mesure.local"
)


# ============================================================
# Acquisition HTTP API
# ============================================================

ACQUISITION_HOST = os.getenv(
    "ACQUISITION_HOST",
    "127.0.0.1"
)

ACQUISITION_PORT = int(
    os.getenv(
        "ACQUISITION_PORT",
        "5100"
    )
)


# ============================================================
# Simulation
# ============================================================

READ_INTERVAL_SECONDS = float(
    os.getenv(
        "READ_INTERVAL_SECONDS",
        "1.0"
    )
)


# ============================================================
# Stability
# ============================================================

STABILITY_TOLERANCE_KG = float(
    os.getenv(
        "STABILITY_TOLERANCE_KG",
        "5.0"
    )
)

STABILITY_REQUIRED_READINGS = int(
    os.getenv(
        "STABILITY_REQUIRED_READINGS",
        "3"
    )
)


# ============================================================
# Weight simulation
# ============================================================

INITIAL_WEIGHT_RATIO = float(
    os.getenv(
        "INITIAL_WEIGHT_RATIO",
        "0.65"
    )
)

CONVERGENCE_RATIO = float(
    os.getenv(
        "CONVERGENCE_RATIO",
        "0.35"
    )
)

INITIAL_NOISE_KG = float(
    os.getenv(
        "INITIAL_NOISE_KG",
        "80.0"
    )
)

FINAL_NOISE_KG = float(
    os.getenv(
        "FINAL_NOISE_KG",
        "1.5"
    )
)

ACTUAL_WEIGHT_MIN_RATIO = float(
    os.getenv(
        "ACTUAL_WEIGHT_MIN_RATIO",
        "0.995"
    )
)

ACTUAL_WEIGHT_MAX_RATIO = float(
    os.getenv(
        "ACTUAL_WEIGHT_MAX_RATIO",
        "1.005"
    )
)


# ============================================================
# Source
# ============================================================

WEIGHT_SOURCE = "OPC-UA-SIMULATION"