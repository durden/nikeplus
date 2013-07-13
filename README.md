# Nikeplus data export

The purpose of this project is to export your
[nike plus](http://nikeplus.nike.com/plus/) data to CSV format.

## Install

- Install package with the standard `pip` workflow:
    - `pip install nikeplusapi`

- Install package for development with the standard `pip` workflow:
    - git clone repositiory
    - cd into repository
    - pip install .

Now you should have a top-level script called `nikeplus`.
Run `nikeplus -h` to verify install worked properly.

## Usage

1. The only requirement for this script is the NikePlus API access token.  You
   can get your token by logging into the
   [Nike developer site](https://developer.nike.com/login/) with your Nike+
   account credentials.
2. You can pass your token via the command-line `-t` option or store it in your
   home directory in a file called `.nikeplus_access_token` that will be read
   automatically when the script executes.
3. This script will output the CSV data directly to `stdout` so you can easily
   re-direct this to a file with the following:
    `nikeplus > backup.csv`.
