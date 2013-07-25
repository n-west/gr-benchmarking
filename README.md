GR Benchmarking
===============

This is a set of tools (based off of scripts available in GNU Radio) to benchmark processors for GNU Radio. 
There are some results provided, that were presented at the New England Workshop for Software Defined Radio on May 2013. 

== Usage
`./run_benchmarking` will run `volk_profile`, then run the benchmarking scripts, then set volk\_profile to use generic kernels and rerun the benchmarks. 

`./plotter.gawk images/plot_manifest.txt` will generate some interesting graphs to look at. (placed in images/ directory)

== Future 
More to come...
