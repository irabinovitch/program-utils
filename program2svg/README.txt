Hideous code for generating the scale program from the schedule feed.

To run:
pip install -r requirements.txt
./program2svg.py 

You'll be prompted for: 
- Day (Thursday, Friday, Saturday, Sunday)
- Room (a list of rooms pulled from the schedule. "all" will grab all rooms)

it will save a file called program.svg with the output.

TODO:
- Make things configurable (eg year, padding, spacing, etc) 
- add CLI arguments so it doesn't have to be interactive
- Auto handle margins / spacing when a schedule spreads across 2 pages 
- Use an actual SVG library instead of just munging xml
