# from django.http import Http404
# from django.template import loader
import requests
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError

from .WBAPI import getWBCountries, getWBMetrics, get_data, display_graph, makeHTMLTable, make_title, get_ylabel
from .bokehGraph import make_bokeh_graph, make_world_map
from .forms import NameForm

from io import BytesIO
import base64
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

All_countries = ["ABW", "AFG", "AGO", "ALB", "AND", "ARE", "ARG", "ARM", "ASM", "ATG", "AUS", "AUT", "AZE",
                 "BDI", "BEL", "BEN", "BFA", "BGD", "BGR", "BHR", "BHS", "BIH", "BLR", "BLZ", "BMU", "BOL", "BRA",
                 "BRB", "BRN", "BTN", "BWA", "CAF", "CAN", "CHE", "CHI", "CHL", "CHN", "CIV", "CMR", "COD", "COG",
                 "COL", "COM", "CPV", "CRI", "CUB", "CUW", "CYM", "CYP", "CZE", "DEU", "DJI", "DMA", "DNK", "DOM",
                 "DZA", "ECU", "EGY", "ERI", "ESP", "EST", "ETH", "FIN", "FJI", "FRA", "FRO", "FSM", "GAB", "GBR",
                 "GEO", "GHA", "GIB", "GIN", "GMB", "GNB", "GNQ", "GRC", "GRD", "GRL", "GTM", "GUM", "GUY", "HKG",
                 "HND", "HRV", "HTI", "HUN", "IDN", "IMN", "IND", "IRL", "IRN", "IRQ", "ISL", "ISR", "ITA", "JAM",
                 "JOR", "JPN", "KAZ", "KEN", "KGZ", "KHM", "KIR", "KNA", "KOR", "KWT", "LAO", "LBN", "LBR", "LBY",
                 "LCA", "LIE", "LKA", "LSO", "LTU", "LUX", "LVA", "MAC", "MAF", "MAR", "MCO", "MDA", "MDG", "MDV",
                 "MEX", "MHL", "MKD", "MLI", "MLT", "MMR", "MNE", "MNG", "MNP", "MOZ", "MRT", "MUS", "MWI", "MYS",
                 "NAM", "NCL", "NER", "NGA", "NIC", "NLD", "NOR", "NPL", "NRU", "NZL", "OMN", "PAK", "PAN", "PER",
                 "PHL", "PLW", "PNG", "POL", "PRI", "PRK", "PRT", "PRY", "PSE", "PYF", "QAT", "ROU", "RUS", "RWA",
                 "SAU", "SDN", "SEN", "SGP", "SLB", "SLE", "SLV", "SMR", "SOM", "SRB", "SSD", "STP", "SUR", "SVK",
                 "SVN", "SWE", "SWZ", "SXM", "SYC", "SYR", "TCA", "TCD", "TGO", "THA", "TJK", "TKM", "TLS", "TON",
                 "TTO", "TUN", "TUR", "TUV", "TZA", "UGA", "UKR", "URY", "USA", "UZB", "VCT", "VEN", "VGB", "VIR",
                 "VNM", "VUT", "WLD", "WSM", "XKX", "YEM", "ZAF", "ZMB", "ZWE"]


def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    countries = getWBCountries()  # get all the countries from the API as a dict
    metrics = getWBMetrics()  # get all the metrics from the API as a dict
    context = {'countries': countries.items(), 'metrics': metrics.items(), 'form': form, }

    return render(request, 'WB/name.html', context)


def index(request):
    countries = getWBCountries()  # get all the countries from the API as a dict
    metrics = getWBMetrics()  # get all the metrics from the API as a dict

    context = {'countries': countries.items(), 'metrics': metrics.items(), }
    return render(request, 'WB/index.html', context)


def graph(request):
    # get the request data
    if 'WorldCheck' in request.GET:
        countries = request.GET.getlist('WorldCheck')

    else:
        countries = request.GET.getlist('states')  # get all the countries selected
    metrics = request.GET.getlist('metrics')  # get all the metrics selected
    start_year = int(request.GET['year1'])
    end_year = int(request.GET['year2'])
    title = request.GET['title']
    xlabel = request.GET['xlabel']
    if xlabel == '':
        xlabel = 'Year'
    ylabel = request.GET['ylabel']
    width = float(request.GET['width'])
    height = float(request.GET['height'])
    # colors = request.GET.getlist('colors')
    # points = request.GET.getlist('points') #should the points be displayed

    if countries[0] == "WholeWorld":
        if len(metrics) > 1:
            return render(request, 'WB/graph.html',
                          {'error': "Please select a single metric when selecting the whole world"})
        pass
        try:
            DF = get_data(All_countries, metrics, start_year, end_year)  # try to get data from WB API
        except requests.exceptions.ConnectionError:
            return render(request, 'WB/graph.html',
                          {
                           'error': "There is a connection error with the World Bank's servers, please try again later."
                          })
        bokeh_script, bokeh_div, inline_resource = make_world_map(DF=DF, metric=metrics, start_year=start_year, end_year=end_year,
                                                 title=title, xlabel=xlabel, ylabel=ylabel)
        #inline_resource = ""
        # make_bokeh_graph(DF=DF, country_codes=countries, metric_list=metrics,
        #                                                             ylabel=get_ylabel(metrics, ylabel),
        #                                                             title=make_title(countries, metrics, start_year,
        #                                                                              end_year),
        #                                                             start_year=start_year,
        #                                                             end_year=end_year)  # get bokeh JS and HTML

        context = {
            'BOKEH_SCRIPT': bokeh_script,
            'BOKEH_DIV': bokeh_div,
            'resources': inline_resource,
            'CSV_FILENAME': './../../data.csv',
            # 'plt': fig,
            # 'extra_info': 'This is extra info',
            # 'CSV': ',' + (DF.to_csv(index=True, header=True)).split('\n', 1)[1]
            # removes numbered cols on the first line
        }
        return render(request, 'WB/graph.html', context)
    try:
        auto_scale = request.GET['auto_year']
    except MultiValueDictKeyError:  # if auto year option not selected it will not be sent with the request
        auto_scale = False

    try:
        black_white = request.GET['BW']
    except MultiValueDictKeyError:  # if black and white option is not selected
        black_white = False

    try:
        DF = get_data(countries, metrics, start_year, end_year)  # try to get data from WB API
    except requests.exceptions.ConnectionError:
        return render(request, 'WB/graph.html',
                      {'error': "There is a connection error with the World Bank's servers, please try again later. "})
    # print(DF)
    is_data = False  # check if there is data across all countries and metrics

    min_year = end_year
    max_year = start_year

    if auto_scale:
        # if len(countries) > 1 and len(metrics) > 1:
        #     DF = DF.T  # transpose the dataframe
        for col in DF.columns[1:]:  # get the first non NaN value in DF across all countries
            for i in range(start_year, min_year):
                if not pd.isnull(DF[col][i]):
                    min_year = i if i < min_year else min_year
                    is_data = True
                    break
            # set end year to last non NaN Value in the dataframe
            for i in range(end_year, max_year + 1, -1):
                try:
                    if not pd.isnull(DF[col][i]):
                        max_year = i if i > max_year else max_year
                        break
                except KeyError:  # if the year is not in the dataframe
                    pass
        if not is_data:  # check if all data in DF is NaN
            print('No data available')
            return render(request, 'WB/graph.html',
                          {'error': 'There is no data available for the selected metrics, countries and years'})
        # start_year = min_year
        # end_year = max_year
        # if len(countries) > 1 and len(metrics) > 1:
        #     DF = DF.T  # return the dataframe to its original orientation
    # create the graph
    display_graph(DF, countries, metrics, min_year, max_year, title, xlabel, ylabel,
                  black_and_white=black_white, height=height, width=width)
    # download_graph(fig, 'graph')
    # download_CSV(DF, 'data')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    # transpose dataFrame
    # del DF.time
    DF.reset_index(drop=True, inplace=True)  # removes row of incorrect years
    DF = DF.T
    DF = DF[list(reversed(DF.columns))]  # flip order of columns in dataframe to start from the oldest year
    DF.rename(index={'Time': 'Year'}, inplace=True)  # rename first row to Year

    bokeh_script, bokeh_div, inline_resource = make_bokeh_graph(DF=DF, country_codes=countries, metric_list=metrics,
                                                                ylabel=get_ylabel(metrics, ylabel),
                                                                title=make_title(countries, metrics, start_year,
                                                                                 end_year),
                                                                start_year=start_year,
                                                                end_year=end_year)  # get bokeh JS and HTML
    # code for viewer

    context = {
        'BOKEH_SCRIPT': bokeh_script,
        'BOKEH_DIV': bokeh_div,
        'resources': inline_resource,
        'GRAPH_IMG': image_base64,
        'CSV_FILENAME': './../../data.csv',
        'table': makeHTMLTable(DF),
        # 'plt': fig,
        # 'extra_info': 'This is extra info',
        'DF': DF,
        'CSV': ',' + (DF.to_csv(index=True, header=True)).split('\n', 1)[1]  # removes numbered cols on the first line
    }

    return render(request, 'WB/graph.html', context)


def render_info(request):
    return render(request, 'WB/info.html')
