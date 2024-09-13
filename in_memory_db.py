import sys
from collections import defaultdict, namedtuple

Checkpoint = namedtuple('Checkpoint', ['value_state', 'count_state'])

data = {}
count_data = defaultdict(int)
undo_log = []

# Build an undo log for operations under a transaction
# We need to save: the prior value v_old stored under k, the prior count of v_old,
# and the prior count of new value v
# Additionally if any of those have already been checkpointed in this transaction scope,
# don't overwrite them. 
def save_state(checkpoint, k, v=None):
    value_state, count_state = checkpoint
    v_old = data.get(k, None)
    count_v_old = count_data[v_old]

    if k not in value_state:
        value_state[k] = v_old
    if v_old not in count_state:
        count_state[v_old] = count_v_old
    if v and v not in count_state:
        count_state[v] = count_data[v]
    
def transact(f, args):
    if len(undo_log) > 0:
        save_state(undo_log[-1], *args)
        #print(undo_log)
    f(*args)

def do_set(k, v):
    v_old = data.get(k, None)
    if v_old:
        count_data[v_old] = count_data[v_old] - 1
    data[k] = v
    count_data[v] = count_data[v] + 1

def do_get(k):
    result = data.get(k, None)
    print(result if result else "NULL")

def do_delete(k):
    if k in data:
        v = data[k]
        del data[k]
        count_data[v] = count_data[v] - 1

def do_count(v):
    print(count_data[v])

def do_end():
    sys.exit(0)

def do_begin_txn():
    undo_log.append(Checkpoint({}, {}))

def do_rollback_txn():
    if len(undo_log) == 0:
        print("TRANSACTION NOT FOUND")
    else:
        checkpoint = undo_log.pop()
        for k, v in checkpoint.value_state.items():
            data[k] = v
        for k, v in checkpoint.count_state.items():
            count_data[k] = v

def do_commit_txns():
    undo_log = []

# Dispatch table for commands
# operation_name: (function, expected_args, is_write_operation)
COMMANDS = {
  'SET':      (do_set, 2, True),
  'GET':      (do_get, 1, False),
  'DELETE':   (do_delete, 1, True),
  'COUNT':    (do_count, 1, False),
  'END':      (do_end, 0, False),
  'BEGIN':    (do_begin_txn, 0, False),
  'ROLLBACK': (do_rollback_txn, 0, False),
  'COMMIT':   (do_commit_txns, 0, False)
}

def parse_and_dispatch(command):
    tokens = command.split()
    op, args = tokens[0], tokens[1:] 
    if op not in COMMANDS:
        sys.exit("Error, unrecognized command: " + str(op))
    fun, argc, is_write = COMMANDS[op]
    if len(args) != argc:
        sys.exit("Error, unexpected arguments: " + str(tokens))

    if is_write:
        transact(fun, args)
    else:
        fun(*args)

if __name__ == '__main__':
    for command in sys.stdin:
        parse_and_dispatch(command)
