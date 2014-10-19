echo "--- Byte compile convertor ---"
pypy -mcompileall otbmxml2sec.py
echo "--- Convertion begin ---"
pypy otbmxml2sec.pyc
echo "--- Convertion done ---"
