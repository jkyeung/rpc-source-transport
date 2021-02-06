'''Compare a source member on SYSTEMA with one on SYSTEMB.

Usage:
    python27/python cmp.py parm('<lib>/<file>(<mbr>)')
or
    python27/python cmp.py parm('<libA>/<fileA>(<mbrA>)' '<libB>/<fileB>(<mbrB>)')

With only one parameter, the two members must have the same library, file,
and member names on both systems.
'''

import sys
import os
import re
import xmlrpclib
from base64 import b64decode

SERVER_IP = '10.x.x.x'  # SYSTEMA
PORT = 8000

member_re = re.compile(r'(.*)/(.*)\((.*)\)')  # library/file(member)

if len(sys.argv) < 2:
    print 'No parameters specified.'
    sys.exit()

m = member_re.match(sys.argv[1].upper())
if not m:
    print 'Could not parse SYSTEMA parameter:', sys.argv[1]
    sys.exit()
from_lib, from_file, from_mbr = m.groups()

if len(sys.argv) > 2:
    m = member_re.match(sys.argv[2].upper())
    if not m:
        print 'Could not parse SYSTEMB parameter:', sys.argv[2]
        sys.exit()
    to_lib, to_file, to_mbr = m.groups()
else:
    to_lib, to_file, to_mbr = from_lib, from_file, from_mbr

# Retrieve the SYSTEMA member.
s = xmlrpclib.ServerProxy("http://{}:{}".format(SERVER_IP, PORT))
try:
    result = s.get(from_lib, from_file, from_mbr)
except IOError:
    print 'Connection failed.'
    sys.exit()
if isinstance(result, basestring):
    print result
    sys.exit()
sys_a = [[line[0], line[1], b64decode(line[2])] for line in result[2]]

# Retrieve the SYSTEMB member.
sys_b = []
f = File400(to_file, 'r', lib=to_lib, mbr=to_mbr)
f.posf()
while not f.readn():
    sys_b.append(f.get())
f.close()

# Compare.
member_a = from_lib + '/' + from_file + '(' + from_mbr + ')'
print "Records in {} on SYSTEMA: {}".format(member_a, len(sys_a))
member_b = to_lib + '/' + to_file + '(' + to_mbr + ')'
print "Records in {} on SYSTEMB: {}".format(member_b, len(sys_b))
if len(sys_a) != len(sys_b):
    print 'Members are different lengths.'
    sys.exit()
if sys_a == sys_b:
    print 'Members are identical.'
    sys.exit()
if all(a[2] == b[2] for a, b in zip(sys_a, sys_b)):
    print 'Members have matching source data.'
    sys.exit()
print 'Members do not match.'
