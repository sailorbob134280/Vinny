# Vinny
## About
Vinny is a program for tracking cellar inventory. It uses Qt for the GUI framework and SQLite as the database. It is still a work in progress, so bugs may be frequent and build distributions are not maintained. More documentation to come once there are fewer bugs. 

## Features
- Barcode generation, printing, and scanning
- Driverless (and cross-platform) label printer support for the Brother QL line of printers (only the QL-500 has been tested so far)
- Import/Export support through Excel spreadsheets
- Location searching
- Bottle history
- Automatic searching and field fill when entering wine data
- Sorting based on many different fields

## Usage
The current recommended way to run Vinny is to download the source, install the requirements by using `pip3 install -r requirements.txt`, and use Python 3 to run the `main.py` file. Maintained builds are coming soon!

## License 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
