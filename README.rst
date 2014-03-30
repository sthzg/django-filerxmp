django-filerxmp
===============

```Status: experimental, currently under development.```
  
    `django-filerxmp` aims to extend supported file metadata available in the database based on data provided by XMP. 

Instead of relying on existing libraries the XMP section of supported file types (currently only images, but the package is actively extended to support audio and video formats) is extracted from the file. This decision was based on incompatibilities between certain Exif/IPTC-NAA boundaries that led to cropped keywords and various other issues.


Status
------

The package is currently in very early development, including experimental parts. For example, it is in current stage only developed against XMP exported by Lightroom 3.5 – 5. Up to now there are no tests included. Once it reaches a ready-to-be-tested state documentation will be extended.

