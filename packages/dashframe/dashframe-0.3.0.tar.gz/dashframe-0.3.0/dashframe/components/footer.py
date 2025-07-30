import dash_bootstrap_components as dbc
from dash import html


def footer(
  customer_name=html.A("USTB", href="https://www.ustb.edu.cn", target="_blank"),
):
  return html.Div(
    dbc.Container(
      [
        html.Footer(
          [
            html.P(
              [
                "© 2025 ",
                customer_name,
                " All rights reserved.",
              ]
            ),
            html.P(
              [
                "Powered by ",
                html.A("Sun Praise, Inc.", href="http://www.sun-praise.com", target="_blank"),
              ]
            ),
          ],
          className="d-flex flex-wrap justify-content-between align-items-center py-3 mt-4 bg-light px-3",
        ),
      ],
    ),
    style={"fontFamily": "Arial, sans-serif", "color": "gray"},
    className="fixed-bottom bg-light",
  )
