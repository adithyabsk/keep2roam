# Google Keep to Roam Daily Notes

![build](https://github.com/adithyabsk/keep2roam/workflows/build/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/adithyabsk/keep2roam/branch/master/graph/badge.svg?token=RPI1KJKN8G)](https://codecov.io/gh/adithyabsk/keep2roam)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/keep2roam?style=plastic)](https://pypi.org/project/keep2roam/)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/keep2roam?style=plastic)](https://pypistats.org/search/keep2roam)
[![GitHub](https://img.shields.io/github/license/adithyabsk/keep2roam?logo=6cc644&style=plastic)](https://github.com/adithyabsk/keep2roam/blob/master/LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Twitter Follow](https://img.shields.io/twitter/follow/adithya_balaji?style=social)](https://twitter.com/intent/follow?screen_name=adithya_balaji)

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
$ pip install keep2roam
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
