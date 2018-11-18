# Routing deliveries using k-means
This collection of scripts was created to assist in routing meal deliveries for a local charitable event. The technique is rather naive, and essentially just utilizes k-means clustering. 

HTML files of the various routes are created, with embeded static maps generated using the Google Maps API

## K-means implementation
All credit for this implementation of the k-means algorithm (Lloyd's algo) goes to the blogger behind "The Data Science Lab":

https://datasciencelab.wordpress.com/tag/lloyds-algorithm/

## Caveats
The six package must be explicitly installed before installing via requirements.txt due to an error in one of this project's dependencies setup.py