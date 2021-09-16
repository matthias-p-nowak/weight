import datetime
import logging
import time

import matplotlib.pyplot
import matplotlib.dates

import completer
import data


def simplePlot(args):
    logging.debug('plotting')
    con=data.checkData()
    rows=con.execute("select datetime(t,'localtime') as tt,w from weight order by tt").fetchall()
    x=[]
    y=[]
    for row in rows:
        t=row[0]
        t=time.strptime(t,"%Y-%m-%d %H:%M:%S")
        t=time.mktime(t)
        dt=datetime.datetime.fromtimestamp(t)
        x.append(dt)
        y.append(row[1])
    fig: matplotlib.pyplot.Figure =None
    sp: matplotlib.pyplot.Axes
    fig,sp=matplotlib.pyplot.subplots()
    sp.plot(x,y)
    for label in sp.get_xticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')
    xfmt = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M')
    sp.xaxis.set_major_formatter(xfmt)
    fig.tight_layout(h_pad=5)
    fig.show()

def init_plot():
    logging.debug('initializing plot module')
    plotOpt=completer.ComplOption('plot')
    completer.rootCompleter.add(plotOpt)
    plotOpt.exec=simplePlot