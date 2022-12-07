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
    data = str(data).strip()
    reg = '^[0-9]+$'
    if re.search(data, reg) or isNumber(data) or is_numeric_dtype(data):
        return 0
    else:
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

def build_bar_chart(dataframe, xAxis, yAxis, chartName):
    trace = go.Bar(showlegend=True)
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

    return figure

def getLayout(xAxis, yAxis, name):
    layout = go.Layout(
        title=name,
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(text=xAxis),
            autorange=True, ticks='', showgrid=False, zeroline=False
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(text=yAxis),
            autorange=True, ticks='', zeroline=False, tickformat=None
        )
    )
    return layout