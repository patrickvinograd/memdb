import sys
from collections import defaultdict

data = {}
count_data = defaultdict(int)
undo_log = []

# For a set in a transaction, we need to record as state:
# - the prior value v_old stored under k, which could be None
# - the prior count of v_old, which could be 0
# - the prior count of v_new, which could be 0
# - and if we set k twice in a transaction:
# - don't want to overwrite v_old
# - save but don't overwrite count_v_old or count_v_new

# SET a foo
# COUNT foo # 1
# BEGIN
# SET a bar # state a:foo, c_foo:1, c_bar:0
# COUNT foo # 0
# COUNT bar # 1
# SET a baz # state a:foo, c_foo:1, c_bar:0, c_baz:0
# COUNT foo # 0
# COUNT bar # 0
# COUNT baz # 1
# SET b baz # state a:foo, b:None, c_foo: 1, c_bar:0, c_baz:0
# COUNT baz # 2
# ROLLBACK
# GET a # foo
# GET b # NULL
# COUNT foo # 1
# COUNT bar # 0
# COUNT baz # 0

# For a delete in a transaction, we need to record as state:
# - the existing value v_old stored under k, which could be None
# - the prior count of v_old, which could be 0
# If two deletes for the same v happen in a transaction:

# SET a foo
# SET b foo
# BEGIN
# DELETE a # state a:foo, c_foo: 2
# DELETE b # state a:foo, b:foo, c_foo: 2
# ROLLBACK
# COUNT foo # 2


def save_state(state, k, v=None):
    value_state, count_state = state
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
    data[k] = v
    count_data[v] = count_data[v] + 1
    if prev:
        count_data[prev] = count_data[prev] - 1

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
    print(count_data.get(v, 0))

def do_begin_txn():
    undo_log.append(({}, {}))

def do_rollback_txn():
    if len(undo_log) == 0:
        print("TRANSACTION NOT FOUND")
    else:
        state = undo_log.pop()
        for k, v in state[0].items():
            data[k] = v
        for k, v in state[1].items():
            count_data[k] = v

def do_commit_txns():
    undo_log = []

def parse_and_execute(command):
    op, args = command.split()[0], command.split()[1:] 
    #print(op, args)
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

#with open(sys.stdin) as f:
for command in sys.stdin:
    parse_and_execute(command)