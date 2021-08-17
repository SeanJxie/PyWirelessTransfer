PORT = 1024

# Message constants ---
BYTESIZE_MSG      = 2   # The size of a regular message.
BYTESIZE_PATHLEN  = 16  # The size of the message holding file path data.
BYTESIZE_NFILES   = 16  # The size of the message holding file quantity.
BYTESIZE_FILESIZE = 128 # The size of the message holding the size of the file.

MSG_CLIENT_CONF   = bytearray(map(ord, "CC"))
MSG_SERVER_CONF   = bytearray(map(ord, "SC"))
MSG_SERVER_REJECT = bytearray(map(ord, "RE"))

