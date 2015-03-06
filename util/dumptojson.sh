for f in testfiles/*.h5
do
  echo "$f"
  s=${f##*/}
  b=${s%.h5}
  python h5tojson.py $f  >json_dump/$b.json
done
