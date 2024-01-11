from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource
import random


def generate_chart(income_data: list = [], expenses_data: list = []):
    # Generate random values
    categories = [str(i) for i in range(1, 31)]
    income_data = [random.randint(1000, 2000) for _ in range(30)]
    expenses_data = [random.randint(500, 1800) for _ in range(30)]

    source = ColumnDataSource(
        data=dict(
            categories=categories, income_data=income_data, expenses_data=expenses_data
        )
    )

    # Create Bokeh figure
    p = figure(
        x_range=categories, height=300, title=None, toolbar_location=None, tools=""
    )

    # Plot income and expenses as grouped bars
    p.vbar(
        x=dodge("categories", -0.18, range=p.x_range),
        top="income_data",
        width=0.3,
        line_color="rgba(75, 192, 192, 1)",
        fill_color="rgba(75, 192, 192, 0.3)",
        legend_label="Income",
        source=source,
    )

    p.vbar(
        x=dodge("categories", 0.2, range=p.x_range),
        top="expenses_data",
        width=0.3,
        line_color="rgba(255, 99, 132, 1)",
        fill_color="rgba(255, 99, 132, 0.3)",
        legend_label="Expenses",
        source=source,
    )

    # Customize plot options
    # p.title.text_color = "gray"
    p.sizing_mode = "scale_width"
    p.height = 150
    p.background_fill_color = None
    p.border_fill_color = None
    p.outline_line_color = None
    p.y_range.start = 0
    p.xgrid.grid_line_width = 0.5
    p.ygrid.grid_line_width = 0.5
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "gray"
    p.yaxis.axis_label = "Amount"
    p.xaxis.axis_label = "Days"
    p.xaxis.axis_label_text_color = "gray"
    p.yaxis.axis_label_text_color = "gray"
    p.xaxis.major_label_text_color = "gray"
    p.yaxis.major_label_text_color = "gray"
    p.xaxis.major_tick_line_color = "gray"
    p.xaxis.minor_tick_line_color = "gray"
    p.yaxis.major_tick_line_color = "gray"
    p.yaxis.minor_tick_line_color = "gray"
    p.xaxis.axis_line_color = None
    p.yaxis.axis_line_color = None
    p.xaxis.axis_label_standoff = 10
    p.legend.background_fill_color = None
    p.legend.label_text_color = "gray"

    # Convert Bokeh plot to components for embedding
    script, chart = components(p)

    return script, chart
