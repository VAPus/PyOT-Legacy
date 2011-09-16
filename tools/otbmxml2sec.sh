echo "--- Byte compile the convertor ---"
python2 -mcompileall otbmxml2sec.py
echo "--- Convertion begin ---"
python2 otbmxml2sec.pyc
echo "--- Byte compile the generated map ---"
python2 -mcompileall genmap.py
echo "--- That was the easy part, now run the generator tool. Notice: this takes alot of memory ---"
python2 genmap.pyc
echo "--- Convertion done ---"
