from tkinter import HORIZONTAL
import nltk
from datetime import datetime
import re
from typing import Pattern
import plotly.graph_objs as go
import plotly.offline as opy
import chardet
import pandas as pd
from dateutil.parser import parse
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_string_dtype

def convert(list):
    return tuple(i for i in list)



def columnType(data):
    if isNumber(data) or is_numeric_dtype(data):
        return 0
    else:
        data = str(data).strip()
        if isDate(data):
            return 1
        else:
            if is_string_dtype(data) or isWord(data):
                return 2
    return 3

def isDate(field, fuzzy=False):
    field = str(field)
    try:
        parse(field, fuzzy=False)
        return True
    except ValueError:
        return False


def isNumber(s):
   try:
       tmp = int(s)
       return True
   except:
       try:
        temp=float(s)
        return True
       except:
        return False


def isWord(field):
    if not isinstance(field, str):
        return False
    return True


def build_scatter_plot(dataframe, category, xAxis, yAxis, chartName):
    trace = go.Scatter(marker=dict(symbol='circle'), mode='markers', showlegend=True)
    layout = getLayout(xAxis, yAxis, chartName)
    figure = go.Figure(data=trace, layout=layout)

    if category:
        figure.update_layout(title=chartName + ' ( ' + (category.lower()) + ')')
        df = dataframe[[category, yAxis, xAxis]]

        # add categories to chart
        unique = df[category].unique()
        for name in unique:
            df2 = dict(tuple(df.groupby(category)))
            df2 = df2[name]
            trace.name = name
            trace.y = df2[yAxis]
            trace.x = df2[xAxis]
            figure.add_trace(trace)
    # No categories: build simple scatter plot
    else:
        trace.y = dataframe[yAxis]
        trace.x = dataframe[xAxis]
        figure.add_trace(trace)
        figure.update_layout(showlegend=False)

    return figure


def build_bar_chart(dataframe, xAxis, yAxis, chartName):
    trace = go.Bar(showlegend=True, )
    layout = getLayout(xAxis, yAxis, chartName)
    figure = go.Figure(data=trace, layout=layout)
    df = dataframe[[yAxis, xAxis]]

    # add traces to chart
    unique = df[xAxis].unique()
    df = dataframe.groupby([xAxis], as_index=False)[yAxis].sum()
    for name in unique:
        df2 = dict(tuple(df.groupby(xAxis)))
        df2 = df2[name]
        trace.name = name
        trace.y = df2[yAxis]
        trace.x = df2[xAxis]
        figure.add_trace(trace)
        figure.layout.xaxis2 = go.layout.XAxis(overlaying="x", 
                                    range=[0, 4], showticklabels=False)
        figure.update_xaxes(showticklabels=False)

    return figure

def getLayout(xAxis, yAxis, name):
    layout = go.Layout(
        title=name,
        hoverdistance=100, # Distance to show hover label of data point
        spikedistance=1000, # Distance to show spike
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(text=xAxis),
            autorange=True, ticks='', showgrid=False, zeroline=False, linecolor="#BCCCDC"
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(text=yAxis),
            autorange=True, ticks='', zeroline=False, tickformat=None, linecolor="#BCCCDC"
        ),
        plot_bgcolor="#FFF",
    )
    return layout