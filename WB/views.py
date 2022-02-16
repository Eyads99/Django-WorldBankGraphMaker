# from django.http import Http404
# from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render  # , get_object_or_404
from .WBAPI import getWBCountries, getWBMetrics, get_data, display_graph, download_graph  # , download_CSV
from .forms import NameForm

import os
from io import BytesIO
import base64
import matplotlib
from wsgiref.util import FileWrapper
import matplotlib.pyplot as plt
import pandas as pd
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

    countries = []
    metrics = []

    # get the request data
    countries.append(request.GET['states'])
    metrics.append(request.GET['metrics'])
    start_year = int(request.GET['year1'])
    end_year = int(request.GET['year2'])
    title = request.GET['title']
    xlabel = request.GET['xlabel']
    if xlabel == '':
        xlabel = 'Year'
    ylabel = request.GET['ylabel']

    try:
        auto_scale = request.GET['auto_year']
    except:
        auto_scale = False

    DF = get_data(countries, metrics, start_year, end_year)
    fig = display_graph(DF, countries, metrics, start_year, end_year, auto_scale, title, xlabel, ylabel)
    #   download_graph(fig, 'graph')
    # download_CSV(DF, 'data')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    # dataFrame = dataFrame.drop([dataFrame.columns[0]], axis=1)

    context = {'GRAPH_IMG': image_base64,
               'CSV_FILENAME': './../../data.csv',
               # 'plt': fig,
               'DF': DF,
               'CSV': DF.to_csv(index=False),
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
