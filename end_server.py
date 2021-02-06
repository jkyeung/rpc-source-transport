import xmlrpclib

SERVER_IP = '10.x.x.x'  # SYSTEMA
PORT = 8000

try:
    s = xmlrpclib.ServerProxy("http://{}:{}".format(SERVER_IP, PORT))
    print s.shutdown()
except IOError:
    print 'Source transport server is already down or refusing requests.'
