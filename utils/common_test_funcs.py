#!/usr/bin/python
#!/usr/bin/env python 

from gnuradio import gr
import math,sys,os,time,re,pickle

try:
    import numpy
except ImportError:
    sys.stderr.write("Unable to import Numpy\n")
    sys.exit(1)

# tables can have names with any letter, number, underscore, period, or dash
table_name_chars = "[()a-zA-Z0-9_. -]"


def common_args(parser):
    parser.add_argument('-D', '--database', type=str, required=True,
                        help='Database (pickled file) to rw results')
    parser.add_argument('--listtables', 
                        default=False, action='store_true',
                        help='print a list of tables in the database file')
    parser.add_argument('--delete', type=str, 
	                help='Delete a table in the database file')

    return parser

def handle_args(conn, args):
    if args.listtables:
        tables = list_tables(conn)
        for t in tables:
            print t
        exit(0)

    if args.delete:
        print "Starting delete process for %s" % args.delete
        tablename = delete_table(conn, args.delete)
        exit(0)


def create_connection(fname):
    '''
    return a file object. If it's not createx
    '''
    try:
        return open(fname,'r+')
    except IOError:
        return open(fname,'w+')

def new_table(conn, tablename):
    '''
    Create a new "table" of sorts for the results. Each table
    should be for a different architecture/machine/type. It's
    best to keep these names unique, but there's no checker
    planned for that.
    You should run list_tables first to make sure that you
    aren't duplicating a table. I don't know what will happen
    '''
    conn.seek(0,os.SEEK_END) # go to end
    # command is the string to write to file
    cmd = "\n<{0}>\n".format(tablename)
    conn.write(cmd)


def insert_results(conn, res):
    '''
    Insert results that are apparently dictionary values into
    the table. Since this is a text file we pickle the list.
    '''
    # because mp-sched was designed to be two independent
    # programs (why oh why oh why?! - fix this later)
    # appending to a file is the "best" way to insert results
    conn.seek(0,2) # go to the last byte in the file
    # the whole dictionary gets pickled
    conn.write("$newdatarow$")
    pickle.dump(res,conn)

def list_tables(conn):
    '''
    return a list of all tables in the database
    '''
    conn.seek(0)
    fstring = conn.read()
    # match as few characters as possible inside angle brackets
    table_names = re.findall("<(.+?)>", fstring)
    return table_names
	
def delete_table(conn, name):
    '''
    Delete a table with the name "tablename" in the database
    '''
    conn.seek(0)
    # fstring = conn.read()
    # print"\n\n\nThis is working so far.\n\n\n"
    # print fstring
    # table ="<("+tablename+">)"
    

    print name
    table = '<'+name+'>\n'
    #print table
    count = 0
    first = 0
    last = 0
    start_found = False
    endOftable = "s.\n"
    print "Are you sure you want to delete the table '%s'?" % table.strip()
    answer = raw_input("(Y/n) ")
    # TODO: rearrange to read entire file first, then delete desired rows
    # Then rewrite file. This has a wasted read for the entire file
    if answer == 'y' or answer == 'Y' or answer == '':
        for line in conn:
            count += 1
            if not start_found and line == (table):
                first = count
                start_found = True
            if start_found and line == "s.\n":
                break
        if start_found:
            last = count
            print "Deleting lines %d through %d" % (first, last)
	
            conn.seek(0)
            data_list = conn.readlines()
            del data_list[(first-1):last]
            conn.seek(0)
            conn.writelines(data_list)
            conn.truncate()
            print"\n<Table deleted>\n"
        else:
            print "Table was not found"
	
    else:
        print"Deletion process aborted...."
        sys.exit(0)

def get_results(conn, tname):
    '''
    gets all results in tname. tname should match an arch+gr version
    No testing is done on originality of tname
    '''
    pickle_string = '(\([a-zA-Z0-9\'\n]*s\.)?'
    conn.seek(0)
    fstring = conn.read()
    # match the < to begin a table
    tables = re.split('(<.*>)?',fstring)
    for i,table in enumerate(tables):
        if table.startswith('<'+tname+'>'):
            res = list()
            entries = re.split("\$newdatarow\$", tables[i+1])
            for row in entries:
                try:
                    rdata = pickle.loads(row)
                except:
                    # yikes! I hope that wasn't data!
                    pass
                else:
                    rdata
                    res.append(rdata)
            return res

def close_connection(conn):
    conn.close()

