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
    prev = data.get(k, None)
    if prev:
        count_data[prev] = count_data[prev] - 1
    data[k] = v
    count_data[v] = count_data[v] + 1

def do_get(k):
    result = data.get(k, None)
    if result:
        print(result)
    else:
        print("NULL")

def do_delete(k):
    if k in data:
        v = data[k]
        del data[k]
        count_data[v] = count_data[v] - 1

def do_count(v):
    print(count_data[v])

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

def parse_and_execute(command):
    tokens = command.split()
    op, args = tokens[0], tokens[1:] 
    if op == 'SET':
        transact(do_set, args)
    elif op == 'GET':
        do_get(*args)
    elif op == 'DELETE':
        transact(do_delete, args)
    elif op == 'COUNT':
        do_count(*args)
    elif op == 'END':
        sys.exit(0)
    elif op == 'BEGIN':
        do_begin_txn()
    elif op == 'ROLLBACK':
        do_rollback_txn()
    elif op == 'COMMIT':
        do_commit_txns()
    else:
        sys.stderr.write("Error, unrecognized command: " + str(op))
        sys.exit(1)

if __name__ == '__main__':
    for command in sys.stdin:
        parse_and_execute(command)
