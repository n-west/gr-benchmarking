#!/usr/bin/python
#!/usr/bin/env python 

from gnuradio import gr, blocks
import math,sys,os,time,re,pickle

try:
    import numpy
except ImportError:
    sys.stderr.write("Unable to import Numpy\n")
    sys.exit(1)


class helper(gr.top_block):
    '''
    Helper function to run the tests. The parameters are:
      N: number of items to process (int)
      op: The GR block/hier_block to test
      isizeof: the sizeof the input type
      osizeof: the sizeof the output type
      nsrcs: number of inputs to the op
      nsnks: number of outputs of the op

    This function can only handle blocks where all inputs are the same
    datatype and all outputs are the same data type
    '''
    def __init__(self, N, op,
                 isizeof=gr.sizeof_gr_complex,
                 osizeof=gr.sizeof_gr_complex,
                 nsrcs=1, nsnks=1):
        gr.top_block.__init__(self, "helper")

        self.op = op
        self.srcs = []
        self.snks = []
        self.head = blocks.head(isizeof, N)

        for n in xrange(nsrcs):
            self.srcs.append(blocks.null_source(isizeof))

        for n in xrange(nsnks):
            self.snks.append(blocks.null_sink(osizeof))

        self.connect(self.srcs[0], self.head, (self.op,0))

        for n in xrange(1, nsrcs):
            self.connect(self.srcs[n], (self.op,n))

        for n in xrange(nsnks):
            self.connect((self.op,n), self.snks[n])

def timeit(tb, iterations):
    '''
    Given a top block, this function times it for a number of
    iterations and stores the time in a list that is returned.
    '''
    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
        print "Warning: failed to enable realtime scheduling"

    times = []
    for i in xrange(iterations):
        start_time = time.time()
        tb.run()
        end_time = time.time()
        tb.head.reset()

        times.append(end_time - start_time)

    return times

def format_results(kernel, times):
    '''
    Convinience function to convert the results of the timeit function
    into a dictionary.
    '''
    res = dict()
    res["kernel"] = kernel
    res["avg"] = numpy.mean(times)
    res["var"] = numpy.var(times)
    res["max"] = max(times)
    res["min"] = min(times)
    return res
