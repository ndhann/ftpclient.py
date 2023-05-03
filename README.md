# ftpclient.py

extremely messy code because i basically wrote all of it in a day


some assumptions i made about arguments:
- 'get' and 'ls' both accept 3 arguments:
`<user>:<password>@<server> <command> <options>`, where `<options>` is either a remote directory or a path to a remote filename
- 'put' accepts 4 arguments:
`<user>:<password>@<server> <command> <dir> <filename>`, where `<dir>` is a remote directory and `<filename>` is a local file to upload.


in general, there's not much, if any, error checking aside from where it could block the output of the FTP server (and even then...)
