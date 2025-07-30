import dash_bootstrap_components as dbc
from dash import Input, Output, callback, html


def gen_examples():
  examples = [
    html.Br(),
    html.H6("Change the value in the text box to see callbacks in action!"),
    html.Div(["Input: ", dbc.Input(id="my-input", value="initial value", type="text")]),
    html.Br(),
    html.Div(id="my-output"),
  ]

  @callback(
    Output(component_id="my-output", component_property="children"),
    Input(component_id="my-input", component_property="value"),
  )
  def update_output_div(input_value):
    return f"Output: {input_value}"

  return examples
