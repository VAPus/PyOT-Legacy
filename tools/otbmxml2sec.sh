echo "--- Convertion begin ---"
python2 -OO otbmxml2sec.py
echo "--- That was the easy part, now run the generator tool. Notice: this takes alot of memory ---"
python2 -OO genmap.py
echo "--- Convertion done ---"
