import dash_bootstrap_components as dbc
from dash import InputGroup, InputGroupText, Input, Button


def compute_id_layout():
  ui = dbc.InputGroup(
    [
      dbc.InputGroupText("Compute ID"),
      dbc.Input(id="compute-id", type="number", placeholder="Input"),
      dbc.Button("Confirm", id="compute-button", color="primary"),
    ],
    className="mb-3",
  )
  return ui