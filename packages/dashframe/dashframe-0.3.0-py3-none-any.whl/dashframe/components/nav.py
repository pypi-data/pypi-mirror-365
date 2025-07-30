import dash_bootstrap_components as dbc


def create_nav(brand: str):
  navbar = dbc.NavbarSimple(
    children=[
      dbc.NavItem(dbc.NavLink("About", href="#")),
      dbc.DropdownMenu(
        children=[
          dbc.DropdownMenuItem("More pages", header=True),
          dbc.DropdownMenuItem("Page 2", href="#"),
          dbc.DropdownMenuItem("Page 3", href="#"),
        ],
        nav=True,
        in_navbar=True,
        label="More",
      ),
    ],
    brand=brand,
    brand_href="#",
    color="primary",
    dark=True,
  )
  return navbar
