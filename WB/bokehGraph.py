import bokeh.models
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, BasicTickFormatter, Legend, GeoJSONDataSource, LinearColorMapper, ColorBar, \
    CustomJS, Slider, CustomJSFilter
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure, show
from bokeh.embed import components
from bokeh.resources import INLINE, CDN
from bokeh.palettes import Category10, brewer
import geopandas as gpd
import json
import pandas as pd
import wbgapi as wb
from .WBAPI import getWBCountries, getWBMetrics


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


def get_geodatasource(gdf):
    """Get getjsondatasource from geopandas object"""
    json_data = json.dumps(json.loads(gdf.to_json()))
    return GeoJSONDataSource(geojson=json_data)


def make_world_map(DF, metric, start_year=1960, end_year=2020, title='', xlabel='Year', ylabel='', ):
    """
    Adapted from code from dmnfarrell.github.io/bioinformatics/bokeh-maps
    :param DF:
    :param metric:
    :param start_year:
    :param end_year:
    :param title:
    :param xlabel:
    :param ylabel:
    :return:
    """

    def merge_dataset(DF_i, gdf, year=2020, key=None, metric_i=None):
        DF_i = DF_i.iloc[2021 - year]  # assumes the latest year is 2021
        # Merge dataframes gdf and df_2016.
        if key is None:
            pass
        DF_i = DF_i.reset_index(level=0)  # add index as a col to merge with gdf
        merged = gdf.merge(DF_i, left_on='country_code', right_on='index', how='inner')

        # rename data column from the year to data
        merged.rename(columns={year: 'data'}, inplace=True)
        return merged

    def bokeh_plot_map(gdf, DF, column=None, year=2020, plot_title=''):
        """Plot bokeh map from GeoJSONDataSource """

        df_i = merge_dataset(DF_i=DF, gdf=gdf, year=year)  # get values for a given year
        geosource = get_geodatasource(df_i)
        palette = brewer['OrRd'][8]
        palette = palette[::-1]
        vals = df_i[df_i.columns[-1]]
        # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
        color_mapper = LinearColorMapper(palette=palette, low=vals.min(), high=vals.max(), low_color=palette[0],
                                         high_color=palette[7])
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20, location=(0, 0),
                             orientation='horizontal')

        tools = 'wheel_zoom,box_zoom,pan,reset'
        p = figure(title=plot_title, plot_height=400, plot_width=850, toolbar_location='right', tools=tools)
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        # Add patch renderer to figure
        p.patches('xs', 'ys', source=geosource, fill_alpha=1, line_width=0.75, line_color='black',
                  fill_color={'field': str(df_i.columns[-1]), 'transform': color_mapper})
        # Specify figure layout.
        p.add_layout(color_bar, 'below')
        return p

    # get geographic data
    shapefile = 'WB/static/WB/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
    # whole of the ne_100m file must be present
    # Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    # Rename columns.
    gdf.columns = ['country', 'country_code', 'geometry']
    gdf = gdf.drop(gdf.index[159])  # remove Antarctica
    gdf = gdf.set_geometry("geometry")

    p = bokeh_plot_map(gdf, DF=DF, column=3, plot_title='')

    # adding year slider below
    tools = 'wheel_zoom,box_zoom,pan,reset'

    # merge GDF with DF data of starting year
    gdf = merge_dataset(DF, gdf, year=start_year)

    slider = Slider(title='Year', value=start_year, start=1961, end=end_year, step=1)

    callback = CustomJS(args=dict(slider=slider, DF=ColumnDataSource(DF), GDF=ColumnDataSource(gdf.drop(gdf.columns[[2]], axis=1))),
                                 code="""
        var time_val = slider.value; //slider year
        // Get the data from the data sources
        const all_data = DF.data;
        const map_data = GDF.data;

        all_data.data = []

        // Update the visible data
        for(var i = 0; i < map_data.data.length; i++) 
        {
            if (all_data.time[i] == time_val)
            {
                map_data.data.push(map_data.x[i]);
            }
        }
        GDF = map_data;
        GDF.change.emit();
    """)



    def update_plot(attr, old, new):
        Current_year = new
        # get data for needed year
        data = DF.T[Current_year]
        gdf.update(merge_dataset(DF_i=data, gdf=gdf, year=Current_year))

    # TODO integrate CUSTOMJS slider
    slider.on_change('value', update_plot)


    layout = p  # error in slider geo data
    script, div = components(layout)  # return JS script and HTML code for world map
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
        tooltip.append(("Value", ("@" + country_list[0])))
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
