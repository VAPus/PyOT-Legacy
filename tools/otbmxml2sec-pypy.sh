echo "--- Convertion begin ---"
pypy otbmxml2sec.py
echo "--- That was the easy part, now run the generator tool. Notice: this takes alot of memory ---"
pypy genmap.py
echo "--- Convertion done ---"
