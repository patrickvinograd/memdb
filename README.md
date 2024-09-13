# memdb
A simple in-memory database exercise based on the provided spec.

## Running

```
python3 in_memory_db.py < INPUT
```

Built and tested with Python3, no dependencies beyond Python standard library.

## Notes

* No specification around what to do for malformed input, so we do some
basic validation of unrecognized commands/arg counts and bail with an 
exit code and message to standard error.

* `test.sh` runs the provided example inputs and diffs them against the 
expected outputs.
