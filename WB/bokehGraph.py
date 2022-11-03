from bokeh.io import save
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show
from bokeh.embed import components
from bokeh.resources import INLINE
import pandas as pd


def make_bokeh_graph(DF, country_codes, metric_list, start_year=1960, end_year=2020, title='', xlabel='Year', ylabel='',
                     height=7, width=35, kind='line', black_and_white=False, ylim=None, xlim=None):
    pass

    source = ColumnDataSource({str(c): v.values for c, v in DF.transpose().items()})

    p = figure(title=title, x_axis_label=xlabel, y_axis_label=ylabel, x_axis_type="datetime")

    p.line(line_width=2, source=source)

    script, div = components(p)

    return script, div, INLINE.render()

    # show(p)

    # return p.line(x=DF.index.values, y=DF, source=ColumnDataSource(DF))

    DF = ColumnDataSource(DF)

    graph = figure(source=DF, title=title, x_axis_label=xlabel, y_axis_label=ylabel)

    # prepare some data
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 2, 4, 5]

    # create a new plot with a title and axis labels
    p = figure(title="Simple line example", x_axis_label="x", y_axis_label="y")

    # add a line renderer with legend and line thickness
    p.line(x, y, legend_label="Temp.", line_width=2)

    # show the results
    return p
