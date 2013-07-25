#!/usr/bin/python
#!/usr/bin/env python

import sys, math
import argparse
import collections
from common_test_funcs import *

try:
    import matplotlib
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Could not import Matplotlib (http://matplotlib.sourceforge.net/)\n")
    sys.exit(1)

def main():
    desc='Plot Volk performance results from a SQLite database. ' + \
        'Run one of the volk tests first (e.g, volk_math.py)'
    parser = argparse.ArgumentParser(description=desc)
#    parser.add_argument('-D', '--database', type=str,
#                        default='volk_results.db',
#                        help='Database file to read data from [default: %(default)s]')
    parser.add_argument('-E', '--errorbars',
                        action='store_true', default=False,
                        help='Show error bars (1 standard dev.)')
    parser.add_argument('-P', '--plot', type=str,
                        choices=['mean', 'min', 'max'],
                        default='mean',
                        help='Set the type of plot to produce [default: %(default)s]')
    parser.add_argument('-%', '--percent', type=str,
                        default=None, metavar="table",
                        help='Show percent difference to the given type [default: %(default)s]')
    parser.add_argument('-T', '--tables', type=str, nargs='*',
                        default=None,
                        help='select the tables to plot')
    parser.add_argument('-o', '--output', type=str, default=" ",
                        help='file to save output to (svg)')
    parser.add_argument('-n', '--normalize', action='store_true', default=False,
                        help='Normalize processing time to number of items [default: false]')
    parser = common_args(parser)
    args = parser.parse_args()
    label = args.tables

    conn = create_connection(args.database)
    handle_args(conn, args)

#    if args.delete:
#        print "\n<Starting deletion process>\n"
#        tablename = delete_table(conn, args.delete)
#        print tablename
#        exit(0)
    # Set up global plotting properties
    matplotlib.rcParams['figure.subplot.bottom'] = 0.2
    matplotlib.rcParams['figure.subplot.top'] = 0.95
    matplotlib.rcParams['figure.subplot.right'] = 0.98
    matplotlib.rcParams['ytick.labelsize'] = 16
    matplotlib.rcParams['xtick.labelsize'] = 16
    matplotlib.rcParams['legend.fontsize'] = 18

    # Get list of tables to compare
    tables = list_tables(conn)
    try:
        if set(args.tables) & set(tables) == set(args.tables):
            tables=args.tables
        else:
            print 'sorry couldnt find all of your tables, try a --listtables'
            exit(0)
    except TypeError:
        print 'Empty list of tables provided, plotting all'

    M = len(tables)

    # Colors to distinguish each table in the bar graph
    # More than 5 tables will wrap around to the start.
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    # b: blue
    # g: green
    # r: red
    # c: cyan
    # m: magenta
    # y: yellow
    # k: black
    # w: white

    # Set up figure for plotting
    f0 = plt.figure(0, facecolor='w', figsize=(14,10))
    s0 = f0.add_subplot(1,1,1)

    # Create a register of names that exist in all tables
    tmp_regs = []
    for table in tables:
        # Get results from the next table
        res = get_results(conn, table)

        tmp_regs.append(list())
        for r in res:
            try:
                tmp_regs[-1].index(r['kernel'])
            except ValueError:
                tmp_regs[-1].append(r['kernel'])

    # Get only those names that are common in all tables
    name_reg = tmp_regs[0]
    for t in tmp_regs[1:]:
        name_reg = list(set(name_reg) & set(t))
    name_reg.sort()

    # Pull the data out for each table into a dictionary
    # we can ref the table by it's name and the data associated
    # with a given kernel in name_reg by it's name.
    # This ensures there is no sorting issue with the data in the
    # dictionary, so the kernels are plotted against each other.
    table_data = collections.OrderedDict()
    for i,table in enumerate(tables):
        # Get results from the next table
        res = get_results(conn, table)

        data = dict()
        for r in res:
            data[r['kernel']] = r

        table_data[table] = data

    if args.percent is not None:
        for i,t in enumerate(table_data):
            if args.percent == t:
                norm_data = []
                for name in name_reg:
                    if(args.plot == 'max'):
                        norm_data.append(table_data[t][name]['max'])
                    elif(args.plot == 'min'):
                        norm_data.append(table_data[t][name]['min'])
                    elif(args.plot == 'mean'):
                        norm_data.append(table_data[t][name]['avg'])


    # Plot the results
    x0 = xrange(len(name_reg))
    i = 0
    # put in to an ordered dict (and order by key) so similar tables come out 
    # with matching colors -- could probably be improved by using orderdict to start
#    table_data = collections.OrderedDict(sorted(table_data.items(), key=lambda t: t[0]))
    for t in (table_data):
        ydata = []
        stds = []
        for name in name_reg:
            stds.append(math.sqrt(table_data[t][name]['var']))
            if(args.plot == 'max'):
                ydata.append(table_data[t][name]['max'])
            elif(args.plot == 'min'):
                ydata.append(table_data[t][name]['min'])
            elif(args.plot == 'mean'):
                ydata.append(table_data[t][name]['avg'])
            if args.normalize is not False:
                ydata[-1] = ydata[-1] / table_data[t][name]['nsamples']
                stds[-1] = stds[-1] / table_data[t][name]['nsamples']


        if args.percent is not None:
            ydata = [-100*(y-n)/y for y,n in zip(ydata,norm_data)]
            if(args.percent != t):
                # makes x values for this data set placement
                # width of bars depends on number of comparisons
                wdth = 0.80/(M-1)
                x1 = [x + i*wdth for x in x0]
                i += 1

                s0.bar(x1, ydata, width=wdth,
                       color=colors[(i-1)%M], label=t,
                       edgecolor='k', linewidth=2)

        else:
            # makes x values for this data set placement
            # width of bars depends on number of comparisons
            wdth = 0.80/M
            x1 = [x + i*wdth for x in x0]
            i += 1

            if(args.errorbars is False):
                s0.bar(x1, ydata, width=wdth,
                       color=colors[(i-1)%M], label=t,
                       edgecolor='k', linewidth=2)
            else:
                s0.bar(x1, ydata, width=wdth,
                       yerr=stds,
                       color=colors[i%M], label=t,
                       edgecolor='k', linewidth=2,
                       error_kw={"ecolor": 'k', "capsize":5,
                                 "linewidth":2})

    nitems = res[0]['nsamples']
    if args.percent is None and args.normalize is False:
        s0.set_ylabel("Processing time (sec) [{0:G} items]".format(nitems),
                      fontsize=22, fontweight='bold',
                      horizontalalignment='center')
    elif args.normalize is True:
        s0.set_ylabel("Processing time (sec)/item [across {0:G} items]".format(nitems),
                      fontsize=22, fontweight='bold',
                      horizontalalignment='center')
    else: #presumably args.percent
        s0.set_ylabel("% Improvement over {0} [{1:G} items]".format(
                args.percent, nitems),
                      fontsize=22, fontweight='bold')

    s0.legend()
    s0.set_xticks(x0)
    s0.set_xticklabels(name_reg)
    for label in s0.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_fontsize(16)

    if args.output == " ":
        plt.show()
    else:
        plt.savefig(args.output, format='pdf')

if __name__ == "__main__":
    main()
