# Readme

## What does this do? 
If you have the specific usecase of sending your photos to another phone to upload to google photos, this will automatically delete photos for you by acting as the relay. 

Photo/Video is sent to whatever device is running this program, which stores that photo/video and makes a copy of it. Once the copy is made, the original is then deleted off the device. Once the copy is succesfully uploaded(checked via google photos API), the copy is also deleted. 

This was made to work with syncthing, as bidirectional bridges will delete it off the other devices as well.

## Requirements
`pyinotify`: monitors the sync folder for new items

## Run Instructions
1. Download the project as a zip folder and extract.
2. run syncfolder.py via `python syncfolder.py`