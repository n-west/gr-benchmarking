#!/usr/bin/python
#!/usr/bin/env python

from gnuradio import gr, blocks
import argparse
from common_test_funcs import *
from volk_test_funcs import *

######################################################################

def float_to_char(N):
    op = blocks.float_to_char()
    tb = helper(N, op, gr.sizeof_float, gr.sizeof_char, 1, 1)
    return tb

######################################################################

def float_to_int(N):
    op = blocks.float_to_int()
    tb = helper(N, op, gr.sizeof_float, gr.sizeof_int, 1, 1)
    return tb

######################################################################

def float_to_short(N):
    op = blocks.float_to_short()
    tb = helper(N, op, gr.sizeof_float, gr.sizeof_short, 1, 1)
    return tb

######################################################################

def short_to_float(N):
    op = blocks.short_to_float()
    tb = helper(N, op, gr.sizeof_short, gr.sizeof_float, 1, 1)
    return tb

######################################################################

def short_to_char(N):
    op = blocks.short_to_char()
    tb = helper(N, op, gr.sizeof_short, gr.sizeof_char, 1, 1)
    return tb

######################################################################

# There is a bug in GR 3.6.5.1 - 3.7.0 that affects char_to_short for aligned data
# http://gnuradio.org/redmine/issues/572 for more info
# for now this has to be gr.char_to_short and test only works in 3.6.5.1 --
def char_to_short(N):
    op = gr.char_to_short()
    tb = helper(N, op, gr.sizeof_char, gr.sizeof_short, 1, 1)
    return tb

######################################################################

def char_to_float(N):
    op = blocks.char_to_float()
    tb = helper(N, op, gr.sizeof_char, gr.sizeof_float, 1, 1)
    return tb

######################################################################

def int_to_float(N):
    op = blocks.int_to_float()
    tb = helper(N, op, gr.sizeof_int, gr.sizeof_float, 1, 1)
    return tb

######################################################################

def complex_to_float(N):
    op = blocks.complex_to_float()
    tb = helper(N, op, gr.sizeof_gr_complex, gr.sizeof_float, 1, 2)
    return tb

######################################################################

def complex_to_real(N):
    op = blocks.complex_to_real()
    tb = helper(N, op, gr.sizeof_gr_complex, gr.sizeof_float, 1, 1)
    return tb

######################################################################

def complex_to_imag(N):
    op = blocks.complex_to_imag()
    tb = helper(N, op, gr.sizeof_gr_complex, gr.sizeof_float, 1, 1)
    return tb

######################################################################

def complex_to_mag(N):
    op = blocks.complex_to_mag()
    tb = helper(N, op, gr.sizeof_gr_complex, gr.sizeof_float, 1, 1)
    return tb

######################################################################

def complex_to_mag_squared(N):
    op = blocks.complex_to_mag_squared()
    tb = helper(N, op, gr.sizeof_gr_complex, gr.sizeof_float, 1, 1)
    return tb

######################################################################


def run_tests(func, N, iters):
    print("Running Test: {0}".format(func.__name__))
    try:
        tb = func(N)
        print "1"
        t = timeit(tb, iters)
        res = format_results(func.__name__, t)
        return res
    except AttributeError:
        print "\tCould not run test. Skipping."
        return None

def main():
    avail_tests = [float_to_char,
                   float_to_int,
                   float_to_short,
                   short_to_float,
                   short_to_char,
                   char_to_short,
                   char_to_float,
                   int_to_float,
                   complex_to_float,
                   complex_to_real,
                   complex_to_imag,
                   complex_to_mag,
                   complex_to_mag_squared]

    desc='Time an operation to compare with other implementations. \
          This program runs a simple GNU Radio flowgraph to test a \
          particular math function, mostly to compare the  \
          Volk-optimized implementation versus a regular \
          implementation. The results are stored to an SQLite database \
          that can then be read by volk_plot.py to plot the differences.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-L', '--label', type=str,
                        default=None,
                        help='Label of database table [default: %(default)s]')
    parser.add_argument('-N', '--nitems', type=float,
                        default=1e9,
                        help='Number of items per iterations [default: %(default)s]')
    parser.add_argument('-I', '--iterations', type=int,
                        default=20,
                        help='Number of iterations [default: %(default)s]')
    parser.add_argument('--tests', type=int, nargs='*',
                        choices=xrange(len(avail_tests)),
                        help='A list of tests to run; can be a single test or a \
                              space-separated list.')
    parser.add_argument('--list', action='store_true',
                        help='List the available tests')
    parser.add_argument('--all', action='store_true',
                        help='Run all tests')
    parser = common_args(parser)
    args = parser.parse_args()

    if(args.list):
        print "Available Tests to Run:"
        print "\n".join(["\t{0}: {1}".format(i,f.__name__) for i,f in enumerate(avail_tests)])
        sys.exit(0)

    N = int(args.nitems)
    iters = args.iterations
    label = args.label

    conn = create_connection(args.database)
    handle_args(conn, args)

    new_table(conn, label)

    if args.all:
        tests = xrange(len(avail_tests))
    else:
        tests = args.tests

    for test in tests:
        res = run_tests(avail_tests[test], N, iters)
        if res is not None:
            res['niters'] = iters
            res['nsamples'] = N
            insert_results(conn, res)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
