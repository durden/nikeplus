# Nikeplus data export

The purpose of this project is to export your
[nike plus](http://nikeplus.nike.com/plus/) data to CSV format.

## Usage

1. Update the ACCESS_TOKEN variable in export.py to your own API key, which you
   can get by logging into the
   [Nike developer site](https://developer.nike.com/login/) with your Nike+
   account credentials.
2. Run `python export.py` to print your Nike+ data in CSV format to the screen.
    - You can easily pipe this to a file for persistent storage: `python
      export.py | nike_plus_backup.csv`
