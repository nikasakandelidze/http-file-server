# Http File Server

Custom HTTP File Server(HFS) implementation. This project is an implementation of a free web server specifically
designed for publishing and sharing files in the network using HTTP 1.1 Protocol.

#  Reference document
While implementing it, [RFC  2616](https://tools.ietf.org/html/rfc2616)  was taken as a reference. 

# Notices
- In "statics" folder, are present different index.html files with styles and scripts in them. 
  By default those folders are set as document roots for the program(specified in config.json),
  and so in the http client(like broswer) upon visiting different vhosts from config.json you'll
  see a directory structure that is present in statics folder.
- In "logs" folder, are present log files which are dynamically generated by http file server during
  the operation time. Logs contain Time,Date,Request type and other useful information.