'''Get data from one member on SYSTEMA into a member on SYSTEMB.

Usage:
    python27/python get.py parm('fromlib/fromfile(frommbr)')
or
    python27/python get.py parm('fromlib/fromfile(frommbr)' 'tolib/tofile(tombr)')

With only one parameter, the FROM location is used for the TO location.

BE CAREFUL!!!  The TO member will be overwritten by the FROM member!
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

# Set up user-friendly strings to use in messages.
to_spec = "{}/{}({})".format(to_lib, to_file, to_mbr)
from_spec = "{}/{}({})".format(from_lib, from_file, from_mbr)

s = xmlrpclib.ServerProxy("http://{}:{}".format(SERVER_IP, PORT))
try:
    result = s.get(from_lib, from_file, from_mbr)
except IOError:
    print 'Connection failed.'
    sys.exit()
if isinstance(result, basestring):
    print result
    sys.exit()

# Try to clear the TO member.  If that fails, assume the member doesn't
# exist and try to add it.
if os.system("clrpfm {}/{} {}".format(to_lib, to_file, to_mbr)):
    if os.system("addpfm {}/{} {}".format(to_lib, to_file, to_mbr)):
        print 'Could not add member:', to_spec
        sys.exit()

# Copy the received data into the member.  Note that the source data has
# been Base64-encoded to make it safe for XML transport.
f = File400(to_file, 'a', lib=to_lib, mbr=to_mbr)
for line in result[2]:
    f['SRCSEQ'] = line[0]
    f['SRCDAT'] = line[1]
    f['SRCDTA'] = b64decode(line[2])
    f.write()
f.close()

# Change the source type and member text.
template = "chgpfm {}/{} {} srctype({}) text('{}')"
os.system(template.format(
    to_lib, to_file, to_mbr, result[0], result[1].replace("'", "''")))

print 'Member copied successfully from SYSTEMA:', from_spec
if to_spec != from_spec:
    print ' => Renamed on SYSTEMB as', to_spec
