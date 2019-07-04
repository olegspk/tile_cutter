OpenStreetMap tile cutter
===========================
Creates a whole image from several OpenStreetMap tiles according to the coordinate of the center point on the map.

INSTALLATION
------------

Run: **pip install -r requirements.txt** on your shell.

CONFIGURATION
-------------
Edit file app_conf.py for change directory to save 'dir_to_save' and URL your tile server 'map_url'.


USAGE
-----

Prepare a CSV file with your data that has three columns: image_id, lat, lon. (Separator ";").

Run keys:  
*-csv*: CSV filename with id, lat, lon.  
*-size*: desired image size.  
*-zoom*: Zoom value on the map.

Example usage:  
Run: **python tile_cutter.py -csv your_data_file.csv -size 224 -zoom 18** on your shell.
