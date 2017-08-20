# send-cli
Unofficial command line (Firefox) Send client

Warning, Sharp Edges!
- overwriting any existing file without additional warning if you accept one as the download name
- uses a huge amount of memory when handling very large files
- your probably going to need to install at least pycryptodomex with pip3, sorry, i don't think its avoidable at the moment? (pycrypto only has AES GCM in a preview release, which i was using initially)
- No error handling, not even http status codes.
- not an exhaustive list, expect serious issues (such as data loss) if precautions are not taken

And plenty of missing features
- no ability to delete uploaded files (just need to print the delete token and add an option to send it)
- no progress information for encryption/transfer
- send urls MUST be quoted at the moment if the key contains "-" characters
- can't read from standard input nor write to standard output
- and more

Issues for bugs/features/mistakes/comments on coding style (using classes etc) are all very welcome, but pull requests more so 😄 

Basic usage
```shell
$ ./send-cli -h
!!! Experimental/alpha quality suitable for testing at your own risk only !!!
usage: send-cli [-h]
                [--service-local | --service-dev | --service-stage | --service-live | --service SERVICE]
                [--file FILE | --url URL]
                [input]

Unofficial (Firefox) Send client

positional arguments:
  input              Uploads or downloads a file specified by path or url, no
                     other options requried

optional arguments:
  -h, --help         show this help message and exit

Set the Send service to used:
  --service-local    Use a Send service at http://localhost:1443/upload
  --service-dev      Use the Send development server for upload
  --service-stage    Use the Send staging server for upload
  --service-live     Use the Send production server for upload (Default)
  --service SERVICE  Specify the url of a Send service to use for upload,
                     should end with /upload

Action:
  --file FILE        Upload the specified file to Firefox Send
  --url URL          Download a file with a Send link

```
