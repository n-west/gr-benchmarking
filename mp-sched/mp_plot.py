#!/usr/bin/python
#!/usr/bin/env python

import sys, math
import argparse
from common_test_funcs import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

try:
    import matplotlib
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Could not import Matplotlib (http://matplotlib.sourceforge.net/)\n")
    sys.exit(1)

def main():
    desc='Plot synthetic FFT/FIR filters from a pickled file of results. ' + \
         'Run one of the synthetic tests first (preferbly with run_benchmarking)'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-T', '--tables', type=str, nargs='*',
                        default=None,
                        help='select the tables to plot')
    parser.add_argument('-o', '--output', type=str, default=" ",
                        help='file to save output to (svg)')


    parser = common_args(parser)
    args = parser.parse_args()
    conn = create_connection(args.database)

    tables = list_tables(conn)
    if(args.listtables):
        for t in tables:
            print t
        exit(0)

    if args.delete:
        print args.delete
        print"\n<Starting deletion process>\n"
        tablename = delete_table(conn, args.delete)
        print tablename
        exit(0)



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
        if tables.__contains__(args.tables[0]):
            tables=args.tables[0]
        else:
            print 'sorry couldnt find all of your tables, try a --listtables'
            print "m-sched plotter"
            print args.tables
            exit(0)
    except TypeError:
        print 'Empty list of tables provided!'
        exit(1)

#    f0 = plt.figure(0, facecolor='w', figsize=(14,14))
#    s0 = f0.add_subplot(1,1,1)
    f1 = plt.figure(1, facecolor='1', figsize=(14,14))
    s1 = f1.add_subplot(111, projection='3d', azim=230)
    

    res = get_results(conn, tables)

    max_stages = 0
    max_pipes = 0
    min_stages = 20
    min_pipes = 20
    results = numpy.zeros((10,10))
    for r in res:
        max_stages = max(max_stages, r['stages'])
        min_stages = min(max_stages, r['stages'])
        max_pipes = max(max_pipes, r['pipes'])
        min_pipes = min(max_pipes, r['pipes'])
        results[r['pipes']-1,r['stages']-1] = r['pseudoflopreal']

#    stages = numpy.arange(min_stages, max_stages)
#    pipes = numpy.arange(min_stages, max_stages)
    stages = numpy.arange(1,11)
    pipes = numpy.arange(1,11)
    pipes3d, stages3d = numpy.meshgrid(pipes, stages)
#    print results.size
#    print pipes.size
#    print stages.size
    surf = s1.plot_surface(pipes3d, stages3d, results, rstride=1, cstride=1,cmap=cm.jet,
                            linewidth=0, antialiased=True)
#    f1.colorbar(surf, shrink=0.5, aspect=5)
#    s1.set_zlim3d(results[min_pipes-1, min_stages-1]/2, results.max()*1.05)
#    contour_plot = s0.contour(pipes,stages,results/(10**9))
    plt.title('GFLOP/sec', fontsize=28)
    plt.xlabel('# pipes', fontsize=20)
    plt.ylabel('# stages', fontsize=20)
#    plt.clabel(contour_plot, inline=1, fontsize=14)

    if args.output == " ":
        plt.show()
    else:
        plt.savefig(args.output, format='pdf')




if __name__ == "__main__":
    main()
