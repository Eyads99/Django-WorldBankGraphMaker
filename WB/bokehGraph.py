from bokeh.models import ColumnDataSource, BasicTickFormatter, Legend
from bokeh.plotting import figure, show
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.palettes import Category10
import pandas as pd
import wbgapi as wb


def make_bokeh_graph(DF, country_codes, metric_list, start_year=1960, end_year=2020, title='', xlabel='Year', ylabel='',
                     height=7, width=35, black_and_white=False):
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

    tooltip = make_tool_tip(metric_list=metric_list, country_list=country_codes, source=source)

    p = figure(title=title, x_axis_label=xlabel, y_axis_label=ylabel, tooltips=tooltip, plot_width=1000)

    if source.column_names[0] == "Year":

        for key in source.data.keys():
            source.data[key] = list(source.data[key])

        for idx, data in enumerate(source.column_names[1:]):  # first row is year
            p.line(x=source.column_names[0], y=data, line_width=2, source=source,
                   legend_label=make_readable_title(data, len(country_codes) > 1, len(metric_list) > 1),
                   color=Category10[10][idx])  # to make line graph
            p.circle(x=source.column_names[0], y=data, source=source,
                     legend_label=make_readable_title(data, len(country_codes) > 1, len(metric_list) > 1),
                     color=Category10[10][idx])  # to put dots on the line graph

        # p.line(x=source.column_names[0], y=source.column_names[1], line_width=2,
        #        source=source)  # to display line graph
        # p.circle(x=source.column_names[0], y=source.column_names[1], source=source)  # to put dots on the line graph
    else:  # multiple countries and metrics
        for idx, data in enumerate(source.column_names[:-1]):
            p.line(x=source.column_names[-1], y=data, line_width=2, source=source,
                   legend_label=make_readable_title(data, True, True), color=Category10[10][idx])  # to make line graph
            p.circle(x=source.column_names[-1], y=data, source=source,
                     legend_label=make_readable_title(data, True, True),
                     color=Category10[10][idx])  # to put dots on the line graph

    p.yaxis.formatter = BasicTickFormatter(use_scientific=False, precision=2)  # prevent use of scientific notation

    p.legend.location = "top_left"
    p.legend.click_policy = "mute"

    script, div = components(p)  # return JS script and HTML code for graph

    return script, div, INLINE.render()


def make_readable_title(data, multiple_countries=False,
                        multiple_metrics=False) -> str:
    if multiple_countries and multiple_metrics:  # if multiple countries and indicators
        data = data.replace("(", "").replace(')', '').replace("'", "").replace(" ", "")  # remove apostrophe and bracket
        title = data.split(',')  # split title elements by comma
        return wb.economy.metadata.get(title[0]).metadata['ShortName'] + ": " \
            + wb.series.metadata.get(title[1]).metadata.get('IndicatorName')

    elif multiple_metrics:  # if multiple countries only
        return wb.series.metadata.get(data).metadata.get('IndicatorName')  # return metric name
    else:
        return wb.economy.metadata.get(data).metadata['ShortName']  # return country name


def make_tool_tip(metric_list, country_list, source):
    tooltip = [
        # ("Value", "@AFG"),
        # ("Year", "@Year")
    ]

    len_metric_list = len(metric_list)
    len_country_list = len(country_list)

    if (len_country_list + len_metric_list) == 2:  # single country single metric
        tooltip.append(("Value", ("@"+country_list[0])))
    elif len_metric_list > 1 and len_country_list > 1:  # multiple countries and metrics
        tooltip = [(make_readable_title(col_name, True, True), "@{" + col_name + "}")
                   for col_name in source.column_names[:-1]]
        tooltip.append(("Year", " @{('Year', '')} "))  # multi country and metric datasource handles years differently
        return tooltip
    elif len_metric_list > 1:  # multiple metrics single country
        tooltip = [(make_readable_title(metric, False, True), "@{" + metric + "}") for metric in metric_list]
    else:  # single metric and multiple countries
        tooltip = [(make_readable_title(country, True, False), "@{" + country + "}") for country in country_list]

    tooltip.append(("Year", "@Year"))
    return tooltip
