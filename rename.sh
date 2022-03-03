#!/bin/sh
# a little script for renaming all *.JPG files to *.jpg

for file in pictures/*.JPG
do
  echo $file 
  mv "$file" "${file/.JPG/.jpg}"
done