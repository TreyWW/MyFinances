from bokeh.plotting import figure
from bokeh.embed import components
import random


def generate_chart(income_data:list=[], expenses_data:list=[]): 
    # Generate random values
    days = ['Day ' + str(i) for i in range(1, 31)]
    income_data = [random.randint(1000, 2000) for _ in range(30)]
    expenses_data = [random.randint(500, 1000) for _ in range(30)]

    # Create a Bokeh figure
    p = figure(x_range=days, height=300, title="Income and Expenses",
               toolbar_location=None, tools="")

    # Plot income and expenses as vertical bars
    p.vbar(x=days, top=income_data, width=0.9, legend_label="Income",
           line_color="white", fill_color="rgba(75, 192, 192, 0.2)")

    p.vbar(x=days, top=expenses_data, width=0.9, legend_label="Expenses",
           line_color="white", fill_color="rgba(255, 99, 132, 0.2)")

    # Customize plot options
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.yaxis.axis_label = "Amount"

    # Convert Bokeh plot to components for embedding
    script, chart = components(p)

    chart = chart.replace('<div', '<div class="w-full h-full bg-gray-100 p-4"')
    print(chart)
    print(script)
    return script, chart