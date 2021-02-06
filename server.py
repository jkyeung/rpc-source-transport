import os
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from base64 import b64encode, b64decode

import os400
import file400

SERVER_IP = '10.x.x.x'  # SYSTEMA
PORT = 8000

# RTVMBRD is a little helper CLP that wraps the RTVMBRD command.
rtvmbrd = os400.Program('RTVMBRD', 'MISEXE',
        (('c', 10), ('c', 10), ('c', 10), ('c', 10), ('c', 512)))

def mbr_text(lib, fil, mbr):
    rtvmbrd(lib, fil, mbr, 'TEXT', '')
    return rtvmbrd[4]

def mbr_srctype(lib, fil, mbr):
    rtvmbrd(lib, fil, mbr, 'SRCTYPE', '')
    return rtvmbrd[4]

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server.
shutdown_request = False
server = SimpleXMLRPCServer((SERVER_IP, PORT), requestHandler=RequestHandler)

def shutdown():
    global shutdown_request
    shutdown_request = True
    return 'Shutdown request submitted.'
server.register_function(shutdown)

def put(from_srctype, from_text, data, to_lib, to_file, to_mbr):
    # Try to clear the member.  If that fails, assume the member doesn't
    # exist and try to add it.
    if os.system("clrpfm {}/{} {}".format(to_lib, to_file, to_mbr)):
        if os.system("addpfm {}/{} {}".format(to_lib, to_file, to_mbr)):
            return 'Could not add member.'
    # Copy the received data into the member.  Note that the source data
    # has been Base64-encoded to make it safe for XML transport.
    f = File400(to_file, 'a', lib=to_lib, mbr=to_mbr)
    for line in data:
        f['SRCSEQ'] = line[0]
        f['SRCDAT'] = line[1]
        f['SRCDTA'] = b64decode(line[2])
        f.write()
    f.close()
    # Change the source type and member text.
    template = "chgpfm {}/{} {} srctype({}) text('{}')"
    os.system(template.format(
        to_lib, to_file, to_mbr, from_srctype, from_text.replace("'", "''")))
    return 'Transfer successful.'
server.register_function(put)

def get(from_lib, from_file, from_mbr):
    data = []
    f = File400(from_file, lib=from_lib, mbr=from_mbr)
    try:
        f.posf()
    except file400.error:
        return 'Could not read member.'
    # If it looks like a source member, Base64-encode the data.
    if f.fieldList() == ('SRCSEQ', 'SRCDAT', 'SRCDTA'):
        while not f.readn():
            data.append((f['SRCSEQ'], f['SRCDAT'], b64encode(f['SRCDTA'])))
    # For any other member, just grab all the fields as-is.
    else:
        while not f.readn():
            data.append(f.get())
    from_text = mbr_text(from_lib, from_file, from_mbr)
    from_srctype = mbr_srctype(from_lib, from_file, from_mbr)
    return from_srctype, from_text, data
server.register_function(get)

# Run the server's main loop.
while not shutdown_request:
    server.handle_request()
