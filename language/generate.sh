echo "MUST BE RUN ON A FRESH REV!"
(
cd ../data/monsters
sed -i 's/genMonster(\"\([^"]*\)\"/genMonster\(_\(\"\1\"\)/g' */*.py */*/*.py */*/*/*.py */*/*/*/*.py */*/*/*/*/*.py 
sed -i 's/genMonster(\(.*\), \"\([^"]*\)\"/genMonster(\1, _(\"\2\")/g' */*.py */*/*.py */*/*/*.py */*/*/*/*.py */*/*/*/*/*.py 
)
xgettext -k_l:2 -k_lp:2,3 -o en_EN.po ../*.py ../*/*.py ../*/*/*.py ../*/*/*/*.py ../*/*/*/*/*.py

(
cd ../data/monsters
hg revert .
)
