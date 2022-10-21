# from django.http import Http404
# from django.template import loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError

from .WBAPI import getWBCountries, getWBMetrics, get_data, display_graph, makeHTMLTable
from .forms import NameForm

from io import BytesIO
import base64
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")


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
    # for key, value in request.GET.items():
    #     print(key, value)
    # extract the data from the request

    # get the request data
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
    except:
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
        start_year = min_year
        end_year = max_year
        # if len(countries) > 1 and len(metrics) > 1:
        #     DF = DF.T  # return the dataframe to its original orientation
    # create the graph
    fig = display_graph(DF, countries, metrics, start_year, end_year, title, xlabel, ylabel,
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

    context = {
        'GRAPH_IMG': image_base64,
        'CSV_FILENAME': './../../data.csv',
        'table': makeHTMLTable(DF),
        # 'plt': fig,
        # 'extra_info': 'This is extra info',
        'DF': DF,
        'CSV': ',' + (DF.to_csv(index=True, header=True)).split('\n', 1)[1]  # removes numbered cols on the first line
    }

    return render(request, 'WB/graph.html', context)


# def download_CSV(request, DF: pd.core.frame.DataFrame):
#     filename = 'data.csv'
#     response = HttpResponse(DF, content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=data.csv'
#
#
#     return response
#     # content = FileWrapper(filename)
#     # response = HttpResponse(content, content_type='application/csv')
#     # response['Content-Length'] = os.path.getsize(filename)
#     # response['Content-Disposition'] = 'attachment; filename=%s' % 'faults.pdf'


def index1(request):
    return render(request, 'WB/info.html')
