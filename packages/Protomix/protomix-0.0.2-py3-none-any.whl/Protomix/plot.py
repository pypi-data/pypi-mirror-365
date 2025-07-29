import plotly.graph_objects as go
import plotly.io as pio

def plot(x, y, title = 'Title', xlabel='Time (s)', ylabel='Intensity (a.u.)', width=800, height=600, color='blue'):    
    # create a scatter plot trace with the given x and y values, using the specified color for the line
    trace = go.Scatter(x=x, y=y, mode='lines', line=dict(width=0.5, color=color))

    # create a layout for the plot with the given title, xlabel, ylabel, width, and height
    layout = go.Layout(title=title,
                       xaxis=dict(title=xlabel, tickfont=dict(family="Calibri", color="blue")),
                       yaxis=dict(title=ylabel, tickfont=dict(family="Calibri", color="blue")),
                       font=dict(family="Times New Roman", color="blue"),
                       legend=dict(title=dict(text='Legend', font=dict(family="Courier New", color="green"))),
                       width=width,
                       height=height)

    # create a new figure object with the trace and layout, and show the plot using Plotly's show method
    fig = go.Figure(data=[trace], layout=layout)
    pio.show(fig)