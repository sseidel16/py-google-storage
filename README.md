# py-google-storage
A project to use Google Photos unlimited storage to store any type of file (byte stream)

## Description
Google has a "high quality" option when saving images to Drive where the images to get downsized (some unknown amount) and the images then do not count toward storage quota. This Python project aims to encode any byte array into pixels and store the image to Drive as "high quality". The project will begin by providing a utility to determine how many bytes can be stored in an image without being lost due to the downsizing performed by Google.

This project may fail, but at least lessons will be learned!
