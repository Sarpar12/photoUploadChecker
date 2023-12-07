# Readme

## What does this do? 
If you have the specific usecase of sending your photos to another phone to upload to google photos, this will automatically delete photos for you by acing as the relay. 

Photo/Video is sent to whatever device is running this program, which stores that photo/video and makes a copy of it. Once the copy is made, the original is then deleted off this device. Once the copy is succesfully uploaded(checked via google photos API), the copy is also deleted. 

If you choose to use syncthing and set up a birectional bridge, then the photos are also deleted off your phone and other device.

## Requirements
`pyinotify`: monitors the sync folder for new items