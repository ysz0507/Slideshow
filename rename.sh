for file in pictures/*.JPG
do
  echo $file 
  mv "$file" "${file/.JPG/.jpg}"
done