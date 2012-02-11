echo "--- Byte compile convertor ---"
pypy -mcompileall otbmxml2sec.py
echo "--- Convertion begin ---"
pypy otbmxml2sec.pyc
echo "--- Byte compile the generated map ---"
pypy -mcompileall genmap.py
echo "--- That was the easy part, now run the generator tool. Notice: this takes alot of memory ---"
pypy genmap.pyc
echo "--- Convertion done ---"
