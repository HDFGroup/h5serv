for f in testfiles/*.h5
do
  echo "$f"
  s=${f##*/}
  b=${s%.h5}
  python exportjson.py -endpoint=127.0.0.1 -port=5000 $b.test.hdfgroup.org >json_dump/$b.json
done
