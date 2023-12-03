import wbgapi as wb
import matplotlib.pyplot  # as plt
import pandas as pd


def getWBCountries() -> dict:
    """
    Makes a dict of all countries IDs and names
    """
    countries = {}  # make a list of countries
    for el in wb.economy.info().__dict__['items']:
        # countries.append((el['id'], el['value']))
        countries[el['id']] = el['value']
    return countries


def getWBMetrics() -> dict:
    """
    Makes a dict of all metrics IDs and names
    """
    metrics = {}  # make a list of metrics
    for el in wb.series.info().__dict__['items']:
        # metrics.append((el['id'], el['value']))
        metrics[el['id']] = el['value']
    return metrics


def get_data(country_codes, metric_codes, start_year=2000, end_year=2020):
    """
    defining function to get data from API
    :param country_codes:
    :param metric_codes:
    :param start_year:
    :param end_year:
    :return: World Bank DataFrame
    """
    if len(country_codes) == 0:
        print('No countries selected')
        return None

    if len(metric_codes) == 0:
        print('No metrics selected')
        return None
    if start_year > end_year:
        print('Start year is greater than end year')
        return None
    if start_year < 1960:
        print('Start year is less than 1960')
        return None
    if end_year > 2022:
        print("End year is greater than current year")
        # return None
    if len(country_codes) > 1 and len(metric_codes) > 1:
        print('Please select a single country and multiple metrics or a single metric and multiple countries')
        # return None

    if len(metric_codes) > 1 and len(country_codes) > 1:
        return wb.data.DataFrame(series=metric_codes, economy=country_codes, time=range(start_year, end_year + 1),
                                 labels=True, index=None, numericTimeKeys=True,
                                 timeColumns=True).T  # not sure what timeColumns does
    else:  # for multiple countries and metrics
        return wb.data.DataFrame(series=metric_codes, economy=country_codes, time=range(start_year, end_year + 1),
                                 labels=True, index=['time'], numericTimeKeys=True,
                                 timeColumns=True)  # not sure what timeColumns does


def display_graph(DF, country_codes, metric_list, start_year, end_year, title='', xlabel='Year', ylabel='',
                  height=7, width=35, kind='line', black_and_white=False):
    """
    make matplot graph
    :param DF:
    :param country_codes:
    :param metric_list:
    :param start_year:
    :param end_year:
    :param title:
    :param xlabel:
    :param ylabel:
    :param height:
    :param width:
    :param kind:
    :param black_and_white:
    :return:
    """

    country_list = [wb.economy.metadata.get(country).metadata['ShortName'] for country in country_codes]

    if DF is None or len(DF) == 0 or DF.empty is True:
        return None

    if title == '':  # if no title is given
        title = make_title(country_codes, metric_list, start_year, end_year)
        ylabel = get_ylabel(metric_list, ylabel)

    if len(metric_list) > 1 and len(country_list) > 1:  # if there are multiple metrics and countries
        # DF = DF.T  # transpose the dataframe
        # prevent no numeric data error
        DF = DF[2:]
        # DF = DF.astype(float)

    if black_and_white:
        # use black for the lines and different markers and line styles
        style = ['ko-', 'ks--', 'kd-.', 'kx:', 'ko', 'k^', 'kv', 'ks', 'kx', 'kd', 'k+', 'k*', 'kp', 'kh', 'kH', 'kD',
                 'k.']
        plot = DF.plot(
            figsize=(width, height),
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            kind=kind,
            # use multiple markers for each series
            style=style
        )
    else:  # normal colour mode
        plot = DF.plot(
            figsize=(width, height),
            ls='solid',
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            kind=kind,
            # use multiple markers for each series
            marker='o',
        )

    # remove scientific notation from y-axis
    plot.ticklabel_format(style='plain', axis='y', useLocale=True)
    plot.set_xticks(range(start_year, end_year + 1))  # to remove 0.5 years
    pd.set_option('display.float_format', lambda x: '%.3f' % x)  # to display 3 decimal places

    #  make appropriate legend
    if len(country_list) > 1 and len(metric_list) > 1:  # if multiple countries and indicators
        metric_labels = [wb.series.metadata.get(metric).metadata.get('IndicatorName') for metric in metric_list]
        legend_list = []
        for metric in metric_labels:
            for country in reversed(country_list):
                legend_list.append(country + ' : ' + metric)
        plot.legend(legend_list, loc='best')

    elif len(country_list) > 1:  # if multiple countries only
        plot.legend(country_list, loc='upper left', bbox_to_anchor=(1, 1))  # list all countries in the legend
    else:
        metric_labels = [wb.series.metadata.get(metric).metadata.get('IndicatorName') for metric in metric_list]
        plot.legend(metric_labels, loc='upper left', bbox_to_anchor=(1, 1))

    plot.bbox_inches = 'tight'  # to remove whitespace around the graph

    # if there is a negative value add dashed line at 0 on Y-axis
    if DF.min(numeric_only=True).min() < 0:
        plot.axhline(y=0, color='black', linestyle='dotted')

    # plt.figure.show()
    return plot


def get_ylabel(metric_list, ylabel=""):
    if ylabel != "":
        return ylabel

    same_unit = False
    metric_name = str(
        wb.series.metadata.get(metric_list[0]).metadata.get('IndicatorName'))  # add first metric name to title
    try:
        metric_name, original_metric_unit = metric_name.split('(', 1)  # if there is a ( in the name
    except ValueError:  # if there is no ( in the name, except used over if statement as most metrics have (
        original_metric_unit = ''
    for metric in metric_list[1:]:
        metric_name = wb.series.metadata.get(metric).metadata.get('IndicatorName')
        try:
            metric_name, metric_unit = metric_name.split('(', 1)
        except ValueError:
            metric_unit = ''
        if metric_unit == original_metric_unit:  # if the same unit is found across all metrics, use it as y-label
            same_unit = True
    if same_unit is True:
        ylabel = original_metric_unit.replace(')', '')
    if len(metric_list) == 1:
        ylabel = original_metric_unit.replace(')', '')
    return ylabel


def make_title(country_codes, metric_list, start_year, end_year):
    title = ""
    country_list = [wb.economy.metadata.get(country).metadata['ShortName'] for country in
                    country_codes]  # make list of country names form their codes
    for country in country_list:  # add a list of all countries to the title
        title += country + ', '
    title = title[:-2] + ' ' + str(start_year) + '-' + str(end_year) + ' '

    test_title = title

    metric_name = str(
        wb.series.metadata.get(metric_list[0]).metadata.get('IndicatorName'))  # add first metric name to title
    # metric_name #+= metric_name
    try:
        metric_name, _ = metric_name.split('(', 1)  # if there is a ( in the name
    except ValueError:  # if there is no ( in the name, except used over if statement as most metrics have (
        pass

    test_title += metric_name
    test_title += ', '

    for metric in metric_list[1:]:
        metric_name = wb.series.metadata.get(metric).metadata.get('IndicatorName')
        try:
            metric_name, _ = metric_name.split('(', 1)  # check if there is no metric uit
        except ValueError:
            pass
        test_title += metric_name
        test_title += ', '
    test_title = test_title[:-2]  # remove last comma and space

    # get title until first opening bracket saving the first half to title and the second half to ylabel
    title = test_title

    return title


def download_graph(plot, file_name='plot', location='', file_format='png'):
    file_name = location + file_name + '.' + file_format  # download the graph as a png file
    plot.figure.savefig(file_name, bbox_inches='tight')


def download_CSV(dataFrame, file_name='data'):
    # Delete first column from CSV before downloading
    # dataFrame = dataFrame.drop([dataFrame.columns[0]], axis=1) # delete first column
    dataFrame.to_csv(file_name + '.csv', na_rep='', index=False)


def makeHTMLTable(dataFrame):
    table = wb.htmlTable(dataFrame)
    table = table.replace('<div class="wbgapi"',
                          '<div class="table table-striped"')  # change tale class to use bootstrap
    return table  # wb.htmlTable(dataFrame)


def get_three_letter_country_codes(country_list):
    """
    param country_list:
    return: list of country codes
    """
    country_codes = []
    for country in country_list:
        country_codes.append(wb.economy.coder(country))  # get the 3-letter code of a given country
        if country_codes[-1] is None:  # in case country is not found
            print(f"{country} not found")
    print(f"country_codes\n{country_codes}")
    return country_codes


def get_metric_codes(metric_list):
    """
    :param metric_list:
    :return:
    """
    metric_codes = []
    for metric in metric_list:

        li = wb.series.info(q=metric)  # search for human-readable name of metric
        li = [var['id'] for var in li.__dict__['items']]
        if len(li) != 0:
            metric_codes.append(li[0])  # add the first metric code to the list if one is found
        else:  # check if the metric is a WB code
            try:
                li = wb.series.get(metric)['id']
                metric_codes.append(li)
            except:
                print(f"{metric} not found")

    print(f"metric_codes\n{metric_codes}")
    return metric_codes
