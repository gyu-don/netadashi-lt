"""Graph coloring problem solver for conference room reservation system."""
from __future__ import annotations

from typing import Any, TypedDict, cast

import dimod
import neal
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


class Reservation(TypedDict):
    """Type of request JSON."""

    name: str
    start: int
    end: int


class ResultJson(TypedDict):
    """Type of response JSON."""

    result: list[list[Reservation]]
    check_constr: bool
    energy: float


def decode(reservations: list[Reservation], n_rooms: int, solution: Any) -> ResultJson:  # noqa: ANN401
    """Decode a result."""
    sample = solution.sample
    result = [[] for _ in range(4)]
    check_constr = True
    for i, r in enumerate(reservations):
        ones = [k for k in range(n_rooms) if sample[f"{k}|{i}"]]
        len_ones = len(ones)
        if len_ones != 1:
            check_constr = False
        if len_ones == 0:
            result[i % 4].append(r)
        else:
            result[ones[i % len_ones]].append(r)
    return {"result": result, "check_constr": check_constr, "energy": solution.energy}


def make_bqm(reservations: list[Reservation], n_rooms: int, param_constr: float) -> dimod.BinaryQuadraticModel:
    """Make a BQM."""
    # constraints
    quad = {}
    linear = {f"{k}|{i}": -param_constr for k in range(n_rooms) for i in range(len(reservations))}
    offset = param_constr * len(reservations)
    for i in range(len(reservations)):
        for j in range(n_rooms):
            for k in range(j + 1, n_rooms):
                quad[f"{j}|{i}", f"{k}|{i}"] = 2 * param_constr
    # objective
    for i in range(len(reservations)):
        for j in range(i + 1, len(reservations)):
            ri = reservations[i]
            rj = reservations[j]
            if min(ri["end"], rj["end"]) > max(ri["start"], rj["start"]):
                for k in range(n_rooms):
                    quad[f"{k}|{i}", f"{k}|{j}"] = 1.0
    return dimod.BinaryQuadraticModel(linear, quad, offset, "BINARY")


@app.route("/hello")
def hello() -> str:
    """Hello returns plain text."""
    return "hello"


@app.route("/solve", methods=["POST"])
def solve() -> Response:
    """Solve the problem."""
    n_rooms = 4
    reservations = cast(list[Reservation], request.get_json())
    bqm = make_bqm(reservations, n_rooms, 10.0)
    sa = neal.SimulatedAnnealingSampler()
    best = sa.sample(bqm, num_reads=50).first
    decoded = decode(reservations, n_rooms, best)
    return jsonify(decoded)
