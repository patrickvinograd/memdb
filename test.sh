#!/bin/bash

for f in examples/example*.txt; do
  echo $(basename $f)
  python3 in_memory_db.py < $f | diff - examples/output_$(basename $f)
  if [[ $? == 0 ]]; then
    echo "PASS"
  else
    echo "FAIL"
  fi
  echo "---"
done
