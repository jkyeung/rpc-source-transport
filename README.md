# rpc-source-transport
Transfer IBM i source members using XML-RPC with iSeriesPython

This project was developed in order to quickly and easily copy source members between our SYSTEMA and SYSTEMB partitions.

[iSeriesPython](https://sourceforge.net/projects/iseriespython/files/Compiled/2.7/revE/) is a port of CPython for IBM midrange (AS/400, iSeries, IBM i) by Per Gummedal. It is unusual in that it is implemented in ILE C and does not involve PASE at all. It has a bunch of features specific to the platform and is a little rough around the edges. It's also stuck at Python 2.7, with no sign of continued development. But it's still a great way to get Python onto machines too old for IBM's own Python offerings for PASE.

If you still use PDM, I highly suggest creating user options to make it quicker and easier to use these Python programs. For example, assuming you've placed them in `/MyDir` on the IFS, you could create the following options (using F16 in PDM) on the client:

    CX    python27/python '/MyDir/cmp.py' parm('&l/&f(&n)')
    GT    python27/python '/MyDir/get.py' parm('&l/&f(&n)')
    PT    python27/python '/MyDir/put.py' parm('&l/&f(&n)')
