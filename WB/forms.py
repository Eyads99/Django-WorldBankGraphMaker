from django import forms
from django_select2 import forms as s2forms

from .WBAPI import getWBMetrics, getWBCountries


# class to make form for the World bank graph maker

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    # countries = forms.CharField(label='Please select a country',
    #                             widget=forms.Select(choices=getWBCountries()))
    # metrics = forms.CharField(label='Please select a metric',
    #                           widget=forms.Select(choices=getWBMetrics()))
    #
    year1 = forms.IntegerField(label='Please select a starting year', min_value=1960, max_value=2022)
    year2 = forms.IntegerField(label='Please select an ending year', min_value=1960, max_value=2022)
    title = forms.CharField(label='Please enter a title for the graph', max_length=100)
    xlabel = forms.CharField(label='Please enter a label for the x-axis', max_length=100)
    ylabel = forms.CharField(label='Please enter a label for the y-axis', max_length=100)

    # def clean(self):
    #     cleaned_data = super().clean()
    #     year1 = cleaned_data.get('year1')
    #     year2 = cleaned_data.get('year2')
    #     if year1 > year2:
    #         raise forms.ValidationError('Year 1 must be less than year 2')
    #     return cleaned_data
