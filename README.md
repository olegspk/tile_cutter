OpenStreetMap tile cutter
===========================
Creates a whole image from several OpenStreetMap tiles according to the coordinate of the center point on the map.

INSTALLATION
------------

Run: **pip install -r requirements.txt** on your shell.

USAGE
-----

Prepare a CSV file with your data that has three columns: image_id, lat, lon. (Separator ";").

Run keys:  
*-url*: URL styles your tile server without {zoom}/{xtile}/{ytile}.png  
*-csv*: CSV filename with id, lat, lon.  
*-sep*: Your CSV separator.  
*-out*: Dir to out created images.
*-size*: Desired image size.  
*-zoom*: Zoom value on the map.

Example usage:  
Run: **python tile_cutter.py -url http://your_tile_server.com:8080/styles/osm-bright -csv your_data.csv -sep ';' -out images_dir -size 224 -zoom 15** on your shell.
