echo "--- Byte compile the convertor ---"
python2 -mcompileall otbmxml2sec.py
echo "--- Convertion begin ---"
python2 otbmxml2sec.pyc
echo "--- Convertion done ---"
