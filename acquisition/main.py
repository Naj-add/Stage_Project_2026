import asyncio
import threading

from flask import (
    Flask,
    jsonify,
    request
)

from .acquisition_service import (
    AcquisitionService
)

from .config import (
    ACQUISITION_HOST,
    ACQUISITION_PORT
)


app = Flask(__name__)

service = AcquisitionService()

loop = None


def start_async_loop():

    global loop

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        service.initialize()
    )

    loop.run_forever()


def run_async(coroutine):

    return asyncio.run_coroutine_threadsafe(
        coroutine,
        loop
    ).result()


# ============================================================
# Health
# ============================================================

@app.get("/health")
def health():

    return jsonify({
        "service": "zeta-mesure-acquisition",
        "status": "UP"
    })


# ============================================================
# Configure operation
# ============================================================

@app.post("/internal/operations/configure")
def configure_operation():

    data = request.get_json()

    if not data:

        return jsonify({
            "message": "Request body is required."
        }), 400

    operation_id = data.get(
        "operation_id"
    )

    sections = data.get(
        "sections"
    )

    if operation_id is None:

        return jsonify({
            "message": "operation_id is required."
        }), 400

    if not sections:

        return jsonify({
            "message": "sections are required."
        }), 400

    try:

        operation = run_async(
            service.configure_operation(
                int(operation_id),
                sections
            )
        )

        return jsonify(
            operation.to_dict()
        ), 201

    except Exception as error:

        return jsonify({
            "message": str(error)
        }), 400


# ============================================================
# Start weighing
# ============================================================

@app.post(
    "/internal/operations/<int:operation_id>/weighing/start"
)
def start_weighing(operation_id):

    data = request.get_json(
        silent=True
    ) or {}

    section_code = data.get(
        "section_code"
    )

    try:

        weighing = run_async(
            service.start_operation(
                operation_id,
                section_code
            )
        )

        return jsonify(
            weighing.to_dict()
        ), 200

    except Exception as error:

        return jsonify({
            "message": str(error)
        }), 400


# ============================================================
# Status
# ============================================================

@app.get(
    "/internal/operations/<int:operation_id>/weighing/status"
)
def weighing_status(operation_id):

    section_code = request.args.get(
        "section_code"
    )

    if section_code:

        weighing = service.get_section(
            operation_id,
            section_code
        )

        if weighing is None:

            return jsonify({
                "message": "Section not found."
            }), 404

        return jsonify(
            weighing.to_dict()
        ), 200

    operation = service.get_operation(
        operation_id
    )

    if operation is None:

        return jsonify({
            "message": "Operation not found."
        }), 404

    return jsonify(
        operation.to_dict()
    ), 200


# ============================================================
# Validate
# ============================================================

@app.post(
    "/internal/operations/<int:operation_id>/weighing/validate"
)
def validate_weighing(operation_id):

    data = request.get_json(
        silent=True
    ) or {}

    section_code = data.get(
        "section_code"
    )

    user_id = data.get(
        "user_id"
    )

    if not section_code:

        return jsonify({
            "message": "section_code is required."
        }), 400

    if user_id is None:

        return jsonify({
            "message": "user_id is required."
        }), 400

    try:

        weighing = run_async(
            service.validate(
                operation_id,
                section_code,
                int(user_id)
            )
        )

        return jsonify(
            weighing.to_dict()
        ), 200

    except Exception as error:

        return jsonify({
            "message": str(error)
        }), 400


# ============================================================
# Cancel
# ============================================================

@app.post(
    "/internal/operations/<int:operation_id>/weighing/cancel"
)
def cancel_weighing(operation_id):

    data = request.get_json(
        silent=True
    ) or {}

    section_code = data.get(
        "section_code"
    )

    if not section_code:

        return jsonify({
            "message": "section_code is required."
        }), 400

    try:

        weighing = run_async(
            service.cancel(
                operation_id,
                section_code
            )
        )

        return jsonify(
            weighing.to_dict()
        ), 200

    except Exception as error:

        return jsonify({
            "message": str(error)
        }), 400


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    async_thread = threading.Thread(
        target=start_async_loop,
        daemon=True
    )

    async_thread.start()

    app.run(
        host=ACQUISITION_HOST,
        port=ACQUISITION_PORT,
        debug=False,
        use_reloader=False
    )