from typing import cast, TypedDict
from flask import Flask, Response, request, jsonify
import neal
import dimod
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class Reservation(TypedDict):
    name: str
    start: int
    end: int


class ResultJson(TypedDict):
    result: list[list[Reservation]]
    check_constr: bool
    energy: float


def decode(reservations: list[Reservation], solution) -> ResultJson:
    bits = solution.sample
    result = [[] for _ in range(4)]
    check_constr = True
    for i, r in enumerate(reservations):
        ci, mi, yi, ki = f"C{i}", f"M{i}", f"Y{i}", f"K{i}"
        bits_sum = bits[ci] + bits[mi] + bits[yi] + bits[ki]
        print(bits[ci], bits[mi], bits[yi], bits[ki])
        if bits_sum == 0:
            check_constr = False
            result[i % 4].append(r)
            continue
        if bits_sum != 1:
            check_constr = False
        if bits[ci]:
            result[0].append(r)
        elif bits[mi]:
            result[1].append(r)
        elif bits[yi]:
            result[2].append(r)
        else:
            result[3].append(r)
    return {"result": result, "check_constr": check_constr, "energy": solution.energy}


def make_qubo(reservations: list[Reservation], param_constr: float) -> tuple[dict[tuple[str, str], float], dict[str, float], float]:
    # constraints
    quad = {}
    linear = {f"{c}{i}": -param_constr for c in "CMYK" for i in range(len(reservations))}
    offset = param_constr * len(reservations)
    for i in range(len(reservations)):
        quad[f"C{i}", f"M{i}"] = 2 * param_constr
        quad[f"C{i}", f"Y{i}"] = 2 * param_constr
        quad[f"C{i}", f"K{i}"] = 2 * param_constr
        quad[f"M{i}", f"Y{i}"] = 2 * param_constr
        quad[f"M{i}", f"K{i}"] = 2 * param_constr
        quad[f"Y{i}", f"K{i}"] = 2 * param_constr
    # objective
    for i in range(len(reservations)):
        for j in range(i + 1, len(reservations)):
            ri = reservations[i]
            rj = reservations[j]
            if min(ri["end"], rj["end"]) > max(ri["start"], rj["start"]):
                quad[f"C{i}", f"C{j}"] = 1.0
                quad[f"M{i}", f"M{j}"] = 1.0
                quad[f"Y{i}", f"Y{j}"] = 1.0
                quad[f"K{i}", f"K{j}"] = 1.0
    return quad, linear, offset


@app.route("/hello/<name>")
def hello(name):
    """hello returns plain text"""
    return "hello " + name

@app.route("/solve", methods=["POST"])
def solve() -> Response:
    reservations = cast(list[Reservation], request.get_json())
    #print(reservations)
    quad, linear, offset = make_qubo(reservations, 10.0)
    bqm = dimod.BinaryQuadraticModel(linear, quad, offset, "BINARY")
    sa = neal.SimulatedAnnealingSampler()
    best = sa.sample(bqm, num_reads=10).first
    decoded = decode(reservations, best)
    #print(decoded)
    return jsonify(decoded)