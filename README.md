# send-cli [![Build Status](https://travis-ci.org/ehuggett/send-cli.svg?branch=master)](https://travis-ci.org/ehuggett/send-cli)
Unofficial command line (Firefox) Send client

![tty_crop](https://user-images.githubusercontent.com/8090731/30059626-c1daf4d4-9237-11e7-97a1-0f53456a293c.gif)

Warning, Sharp Edges!
- will overwrite the output file without warning, but does prompt for the output filename
- Uses temp files to avoid using large amount of memory, you will need at least 2GB of free disk space to upload a 2GB file
- Very limited error checking
- expect serious issues such as data loss if precautions are not taken (you are using a service where destroying your data is a feature, use common sense)

Issues for bugs/features/mistakes/comments on coding style are all very welcome, please also feel free to open pull requests for nits/petty changes.

Basic usage
```shell
$ send-cli -h
!!! Experimental/alpha quality suitable for testing at your own risk only !!!
usage: send-cli [-h]
                [--service-local | --service-dev | --service-stage | --service-live | --service SERVICE]
                [--file FILE | --stdin FILENAME | --delete URL TOKEN | --url URL]
                [--ignore-version]
                [input]

Unofficial (Firefox) Send client

positional arguments:
  input               Uploads or downloads a file specified by path or url, no
                      other options required

optional arguments:
  -h, --help          show this help message and exit
  --ignore-version    Disable server version checks (MAY CAUSE LOSS OF DATA)

Set the Send service to used:
  --service-local     Use a Send service at http://localhost:8080
  --service-dev       Use the Send development server for upload
  --service-stage     Use the Send staging server for upload
  --service-live      Use the Send production server for upload (Default)
  --service SERVICE   Specify the url of a Send service to use for upload, can
                      also be set with the environment variable SEND_SERVICE

Action:
  --file FILE         Upload the specified file to Firefox Send
  --stdin FILENAME    Upload data read from standard input with this filename
  --delete URL TOKEN  Delete a file hosted on a Send server
  --url URL           Download a file with a Send link
```
