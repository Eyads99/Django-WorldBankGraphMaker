from bokeh.models import ColumnDataSource, BasicTickFormatter
from bokeh.plotting import figure, show
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.palettes import Category10
import pandas as pd
import wbgapi as wb


def make_bokeh_graph(DF, country_codes, metric_list, start_year=1960, end_year=2020, title='', xlabel='Year', ylabel='',
                     height=7, width=35, kind='line', black_and_white=False):
    if DF is None or len(DF) == 0 or DF.empty is True:
        return None

    if len(metric_list) > 1 and len(country_codes) > 1:  # if there are multiple metrics and countries
        # DF = DF.T  # transpose the dataframe
        # prevent no numeric data error
        DF.drop(DF.columns[len(DF.columns) - 2:len(DF.columns)], axis=1, inplace=True)  # delete last 2 rows
        DF = DF.T
        years = list(range(end_year, start_year - 1, -1))  # years = list(range(end_year, start_year-1,-1))
        DF['Year'] = years
        DF = DF.T

    source = ColumnDataSource({str(c): v.values for c, v in DF.transpose().items()})

    p = figure(title=title, x_axis_label=xlabel, y_axis_label=ylabel)

    if source.column_names[0] == "Year":
        for idx, data in enumerate(source.column_names[1:]):  # first row is year
            p.line(x=source.column_names[0], y=data, line_width=2, source=source,
                   legend_label=make_legend_title(data, len(country_codes) > 1, len(metric_list) > 1),
                   color=Category10[10][idx])  # to make line graph
            p.circle(x=source.column_names[0], y=data, source=source,
                     legend_label=make_legend_title(data), color=Category10[10][idx])  # to put dots on the line graph

        p.line(x=source.column_names[0], y=source.column_names[1], line_width=2,
               source=source)  # to display line graph
        p.circle(x=source.column_names[0], y=source.column_names[1], source=source)  # to put dots on the line graph
    else:  # multiple countries and metrics
        for idx, data in enumerate(source.column_names[:-1]):
            p.line(x=source.column_names[-1], y=data, line_width=2, source=source,
                   legend_label=make_legend_title(data, True, True), color=Category10[10][idx])  # to make line graph
            p.circle(x=source.column_names[-1], y=data, source=source,
                     legend_label=make_legend_title(data, True, True),
                     color=Category10[10][idx])  # to put dots on the line graph

    p.yaxis.formatter = BasicTickFormatter(use_scientific=False, precision=2)  # prevent use of scientific notation


    script, div = components(p)

    return script, div, INLINE.render()


def make_legend_title(data, multiple_countries=False, multiple_metrics=False) -> str:  # TODO read country code & metric

    if multiple_countries and multiple_metrics:  # if multiple countries and indicators
        data = data.replace("(", "").replace(')', '').replace("'", "").replace(" ",
                                                                               "")  # remove apostrophes and brackets
        title = data.split(',')  # split title elements by comma
        return wb.economy.metadata.get(title[0]).metadata['ShortName'] + ": " \
            + wb.series.metadata.get(title[1]).metadata.get('IndicatorName')

    elif multiple_metrics:  # if multiple countries only
        return wb.series.metadata.get(data).metadata.get('IndicatorName')  # return metric name
    else:
        return wb.economy.metadata.get(data).metadata['ShortName']  # return country name
