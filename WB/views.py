# from django.http import Http404
# from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render  # , get_object_or_404
from .WBAPI import getWBCountries, getWBMetrics, get_data, display_graph, download_graph, \
    makeHTMLTable  # , download_CSV
from .forms import NameForm

import os
from io import BytesIO
import base64
import matplotlib
from wsgiref.util import FileWrapper
import matplotlib.pyplot as plt
import pandas as pd
import wbgapi as w
import csv

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
    # width = reuqest.GET['width']
    # height = request.GET['height']
    # colors = request.GET.getlist('colors')
    # points = request.GET.getlist('points') #should the points be displayed

    try:
        auto_scale = request.GET['auto_year']
    except:
        auto_scale = False

    DF = get_data(countries, metrics, start_year, end_year)

    if auto_scale:
        for country in countries:  # get the first non NaN value in DF across all countries
            for i in range(start_year, end_year):
                if not pd.isnull(DF[country][i]):
                    start_year = i
                    break

            # set end year to last non NaN Value in the dataframe
            for i in range(end_year, start_year, -1):
                try:
                    if not pd.isnull(DF[country][i]):
                        end_year = i
                        break
                except KeyError:  # if the year is not in the dataframe
                    pass

    # create the graph
    fig = display_graph(DF, countries, metrics, start_year, end_year, title, xlabel, ylabel)
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
    # print(DF)

    context = {
        'GRAPH_IMG': image_base64,
        'CSV_FILENAME': './../../data.csv',
        'table': makeHTMLTable(DF),
        # 'plt': fig,
        'DF': DF,
        'CSV': DF.to_csv(index=True, header=True),
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
    return render(request, 'WB/index1.html')
