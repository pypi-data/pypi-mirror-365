import json

def export_state_to_json(state):
    """
    Convert internal game state to a JSON-serializable dict for 3D rendering.
    """
    return json.dumps({
        "positions": [{"x": x, "y": y} for (x, y) in state["positions"]],
        "horiz_walls": [{"x": x, "y": y} for (x, y) in state["horiz_walls"]],
        "vert_walls": [{"x": x, "y": y} for (x, y) in state["vert_walls"]],
        "walls_remaining": state["walls_remaining"],
        "turn": state["turn"],
        "winner": state["winner"]
    }, indent=2)

def save_state_to_file(state, filename):
    with open(filename, "w") as f:
        f.write(export_state_to_json(state))

def load_state_from_file(filename):
    with open(filename, "r") as f:
        return json.load(f)
