PORT = 1024 # Random free port.

# Message constants ---
BYTESIZE_MSG       = 2 
BYTESIZE_PATH_SIZE = 64 # The size of the file path being transfered.
BYTESIZE_NFILES    = 64 # The number of files being transfered.
BYTESIZE_FILESIZE  = 128 # The size of the file being transfered

MSG_CLIENT_CONF   = bytearray(map(ord, "CC"))
MSG_SERVER_CONF   = bytearray(map(ord, "SC"))
MSG_SERVER_REJECT = bytearray(map(ord, "RE"))
