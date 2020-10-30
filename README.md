# Google Keep to Roam Date Files

Converts a Google Takeout dump of Google Keep to daily notes pages for the day
that each snippet was written.

* Tested on Python 3.7.9
* Requires marshmallow `pip install -r requirements.txt`

## Usage

```console
$ python convert.py [KEEP_DUMP] [OUTPUT_FOLDER]
```

## Upload Limit

To upload more than 10 files at a time, use this workaround:

* https://forum.roamresearch.com/t/workaround-for-10-file-limit-on-markdown-import/558/2
