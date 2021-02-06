'''Put data from one member on SYSTEMB into a member on SYSTEMA.

Usage:
    python27/python put.py parm('fromlib/fromfile(frommbr)')
or
    python27/python put.py parm('fromlib/fromfile(frommbr)' 'tolib/tofile(tombr)')

With only one parameter, the FROM location is used for the TO location.

BE CAREFUL!!!  The TO member will be overwritten by the FROM member!
'''

import sys
import re
import xmlrpclib
from socket import error as SocketError
from base64 import b64encode

import os400
from file400 import error as File400Error

SERVER_IP = '10.x.x.x'  # SYSTEMA
PORT = 8000

member_re = re.compile(r'(.*)/(.*)\((.*)\)')  # library/file(member)

# RTVMBRD is a little helper CLP that wraps the RTVMBRD command.
rtvmbrd = os400.Program('RTVMBRD', 'MISEXE',
        (('c', 10), ('c', 10), ('c', 10), ('c', 10), ('c', 512)))

def mbr_text(lib, fil, mbr):
    rtvmbrd(lib, fil, mbr, 'TEXT', '')
    return rtvmbrd[4]

def mbr_srctype(lib, fil, mbr):
    rtvmbrd(lib, fil, mbr, 'SRCTYPE', '')
    return rtvmbrd[4]

if len(sys.argv) < 2:
    print 'No parameters specified.'
    sys.exit()

m = member_re.match(sys.argv[1].upper())
if not m:
    print 'Could not parse FROM parameter:', sys.argv[1]
    sys.exit()
from_lib, from_file, from_mbr = m.groups()

if len(sys.argv) > 2:
    m = member_re.match(sys.argv[2].upper())
    if not m:
        print 'Could not parse TO parameter:', sys.argv[2]
        sys.exit()
    to_lib, to_file, to_mbr = m.groups()
else:
    to_lib, to_file, to_mbr = from_lib, from_file, from_mbr

f = File400(from_file, lib=from_lib, mbr=from_mbr)
try:
    f.libName()
except File400Error:
    print 'Cannot open FROM member:', sys.argv[1]
    sys.exit()

data = []
f.posf()
while not f.readn():
    data.append((f['SRCSEQ'], f['SRCDAT'], b64encode(f['SRCDTA'])))
from_text = mbr_text(from_lib, from_file, from_mbr)
from_srctype = mbr_srctype(from_lib, from_file, from_mbr)

s = xmlrpclib.ServerProxy("http://{}:{}".format(SERVER_IP, PORT))
try:
    print s.put(from_srctype, from_text, data, to_lib, to_file, to_mbr)
except SocketError:
    print 'Connection failed.'
    sys.exit()
