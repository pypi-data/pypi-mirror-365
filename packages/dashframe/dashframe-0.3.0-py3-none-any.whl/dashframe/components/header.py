import dash_bootstrap_components as dbc
from dash import html


def create_header(text: str):
  return html.P([text], className="my-2", style={"fontWeight": "bold"})
