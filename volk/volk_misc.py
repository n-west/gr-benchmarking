#!/usr/bin/python
#!/usr/bin/env python

from gnuradio import gr, digital, analog, filter
import argparse, os
from common_test_funcs import *
from volk_test_funcs import *


def bpsk_demod(N):
    op = digital.bpsk.bpsk_demod( differential=True,
              samples_per_symbol=4,
              excess_bw=0.35,
              phase_bw=6.28/100.0,
              timing_bw=6.28/100.0,
              gray_coded=True,
              verbose=False,
              log=False,
              )

    tb = helper(N/10, op, gr.sizeof_gr_complex, gr.sizeof_char, 1, 1)
    return tb


def qam64_demod(N):
    op = digital.bpsk.bpsk_demod( constellation_points=64,
              differential=True,
              samples_per_symbol=4,
              excess_bw=0.35,
              phase_bw=6.28/100.0,
              timing_bw=6.28/100.0,
              verbose=False,
              log=False,
              )

    tb = helper(N/10, op, gr.sizeof_gr_complex, gr.sizeof_char, 1, 1)
    return tb


def descrambler(N):
    op = gr.descrambler_bb(0x8a, 0x7F, 7)
    tb = helper(N/1, op, gr.sizeof_char, gr.sizeof_char, 1, 1)
    return tb

def agc(N):
    op = analog.agc_cc()
    tb = helper(N/10, op, gr.sizeof_gr_complex, gr.sizeof_gr_complex, 1, 1)
    return tb

def pfb_arb_resampler(N):
    op = filter.pfb.arb_resampler_ccf(2, taps=None, flt_size=32)
    tb = helper(N/10, op, gr.sizeof_gr_complex, gr.sizeof_gr_complex, 1, 1)
    return tb

def clock_recovery(N):
    op = digital.clock_recovery_mm_cc(2, 0.001, 0.5, 0.01, 0.001)
    tb = helper(N/10, op, gr.sizeof_gr_complex, gr.sizeof_gr_complex, 1, 1)
    return tb

######################################################################

def run_tests(func, N, iters):
    print("Running Test: {0}".format(func.__name__))
    try:
        tb = func(N)
        t = timeit(tb, iters)
        res = format_results(func.__name__, t)
        return res
    except AttributeError:
        print "\tCould not run test. Skipping."
        return None

def main():
    avail_tests = [ bpsk_demod,
                    descrambler,
                    qam64_demod,
                    agc,
                    pfb_arb_resampler,
                    clock_recovery
                    ]

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
    if(args.listtables):
        tables = list_tables(conn)
        for t in tables:
            print t
        exit(0)

    if args.delete:
	print"\n<Starting deletion process>\n"
        tablename = delete_table(conn, label)    
	print tablename
	exit(0)

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
