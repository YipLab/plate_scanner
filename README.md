# plate_scanner
An automated multi-wellplate imaging system for high content, high resolution brightfield imaging. The current system acquires a 96 wellplate in less than 3 minutes at an effective pixel size of 2.7 um/px and acquires a well of a 96 wellplate in 4096 x 4096 pixels.  
## Working principle
Our system employs a line scan camera and requires the system to be continuously running as the camera is acquiring,  just like a scanner. This means that we acquire a entire row of the 96 wellplate in a single run and individual wells can be split up using post-processing. Below is a comparison between a smaller area sensor versus a line sensor:

Since our system needs to be continuosly moving, a traditional setup where moving the wellplate will induce vibrational artifacts in the image. We opted to put the optics on an xy stage to move the optics as the line scan camera is acquring. As it is a brightfield system, the optical configuration of the system is pretty simple:  

![System Schematic](/images/schematic.png)

TODO:  
ADD FIGURE  

## Prototype 1
The first system was purpose built for C. elegans phenotypic studies, specifically used for a small molecule screen to identify potential molecules that inhibit their egg laying behaviour.  

![Prototype 1](/images/prototype1.png)

## Prototype 2
The second device is a more refined prototype with a smaller footprint. This allowed the device to be transported the device to its new home in the Thibault Lab at the Nanyang Technical University in November 2017.  

![Prototype 2](/images/prototype2.png)


Files for Plate Reader

TODO:
Serial command documentation for motor
GUI documentation
