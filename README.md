# Google Keep to Roam Daily Notes

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/adithyabsk/keep2roam/build?color=6cc644&logo=github&style=plastic)
![Codecov](https://img.shields.io/codecov/c/github/adithyabsk/keep2roam?color=6cc644&style=plastic)
![GitHub](https://img.shields.io/github/license/adithyabsk/keep2roam?logo=6cc644&style=plastic)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Twitter Follow](https://img.shields.io/twitter/follow/adithya_balaji?style=social)

Convert a Takeout of Google Keep to Roam Daily Notes for the day that each
snippet was written. If multiple notes were written on the same day, they are
merged together.

## Installation

First, go to [Google Takeout](https://takeout.google.com/settings/takeout) and
request a dump of your Google Keep data. Then unzip the folder that Google sends
you.

The following steps work well on Unix systems but on Windows it would be quite
similar.

```console
$ cd ~/Downloads
$ tar -xvf takeout-{ID}.zip
$ pip install git+https://github.com/adithyabsk/keep2roam.git
$ mkdir markdown
$ k2r -h
Usage: k2r [OPTIONS] SRC DEST

  Convert SRC Google Keep Takeout dump and write to DEST folder.

  Assumes SRC exists and creates DEST folder if it does not exist.

Options:
  --version   Prints the CLI version
  -h, --help  Show this message and exit.
$ k2r Takeout/Keep markdown
Found X Google Keep json files...
```

## Upload Limit

Now take these files and upload them to Roam. To upload more than 10 files at a
time, use [this workaround.](https://forum.roamresearch.com/t/workaround-for-10-file-limit-on-markdown-import/558/2)
