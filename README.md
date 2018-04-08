# send-cli [![Build Status](https://travis-ci.org/ehuggett/send-cli.svg?branch=master)](https://travis-ci.org/ehuggett/send-cli)
Unofficial command line (Firefox) Send client

![tty_crop](https://user-images.githubusercontent.com/8090731/30059626-c1daf4d4-9237-11e7-97a1-0f53456a293c.gif)

Warning, Sharp Edges!
- will overwrite the output file without warning, but does prompt for the output filename
- Uses temp files to avoid using large amount of memory, you will need at least 2GB of free disk space to upload a 2GB file
- Very limited error checking
- expect serious issues such as data loss if precautions are not taken (you are using a service where destroying your data is a feature, use common sense)

Issues for bugs/features/mistakes/comments on coding style are all very welcome, please also feel free to open pull requests for nits/petty changes.

## Installation
You can install the package "[sendclient](https://pypi.python.org/pypi/sendclient)" from the python package index
```shell
pip3 install sendclient
```
or from a clone of this repository
```shell
pip3 install /path/to/cloned/send-cli/
```
_tip: use `pip install -e` to install in 'editable' mode if your intending to modify the client_

## Basic usage
```shell
$ send-cli -h
!!! Experimental/alpha quality suitable for testing at your own risk only !!!
usage: send-cli [-h]
                [--service-local | --service-dev | --service-stage | --service-live | --service SERVICE]
                [--file FILE | --stdin FILENAME | --delete URL TOKEN | --change-download-limit URL TOKEN LIMIT | --change-password URL TOKEN | --url URL]
                [--ignore-version] [--download-limit LIMIT]
                [--password | --password-unsafe PASSWORD_UNSAFE]
                [input]

Unofficial (Firefox) Send client

positional arguments:
  input                 Uploads or downloads a file specified by path or url,
                        no other options required

optional arguments:
  -h, --help            show this help message and exit
  --ignore-version      Disable server version checks (MAY CAUSE LOSS OF DATA)
  --download-limit LIMIT
                        Download limit for the uploaded file. Should be <=20

Set the Send service to used:
  --service-local       Use a Send service at http://localhost:8080
  --service-dev         Use the Send development server for upload
  --service-stage       Use the Send staging server for upload
  --service-live        Use the Send production server for upload (Default)
  --service SERVICE     Specify the url of a Send service to use for upload,
                        can also be set with the environment variable
                        SEND_SERVICE

Action:
  --file FILE           Upload the specified file to Firefox Send
  --stdin FILENAME      Upload data read from standard input with this
                        filename
  --delete URL TOKEN    Delete a file hosted on a Send server
  --change-download-limit URL TOKEN LIMIT
                        Change the download limit for a file hosted on a Send
                        server, LIMIT must be <=20
  --change-password URL TOKEN
                        change the password for a file hosted on a Send server
  --url URL             Download a file with a Send link

Password:
  --password            Protect the uploaded file with a password
  --password-unsafe PASSWORD_UNSAFE
                        Provide a password on the command-line (UNSAFE as
                        password visible in process list or shell history!)
```
## Miscellaneous

### Reading command line arguments from a file
Filenames on the command line prefixed with '@' will be replaced by the arguments they contain. This is handled by argparse
https://docs.python.org/3/library/argparse.html#fromfile-prefix-chars

Example formatting
```
--service
https://your-send.server/
--password
--file
path/to/file
```
or
```
--service=https://your-send.server/
--password
--file=path/to/file
```

Multiple files can be included in the same command
```bash
send-cli @file1 @file2 --file path/to/file
```

### Don't put secrets on the command line!
You can avoid secrets (such as passwords or Send URLs) being recorded in your shell history or exposed via `/proc/PID/cmdline`by either
- having send-cli prompt you for it (e.g. `--password`)
- reading it from a file (e.g. `--password-unsafe @password-file`) if it has to be done non-interactively.

_tip: Instead of a regular file, you can avoid writing the password to disk by using a named pipe (_`mkfifo`_)_
### Password Length
When uploading a file the Send UI prevents the uploading user from entering a password longer than 32 characters.
send-cli does not enforce this limit but remains 'compatible' as Send does not currently limit password length when downloading a file.
