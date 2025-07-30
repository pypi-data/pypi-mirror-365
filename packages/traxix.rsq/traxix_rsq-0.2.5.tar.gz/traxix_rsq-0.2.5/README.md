# rsq

Really Simple Queue is a really simple queue. 
It allows to push work in an async queue. Workers can consume that queue, and submit results. 

## Requirements

* Mongo >= 3


## Usage

### Python 

```py
from traxix.rsq import RSQ, Const

# Init
rsq = RSQ(mongo_url="localhost")

# Push work
rsq.push(foo="bar")

# Get work
work = rsq.pull()

# Send result
rsq.done(_id=work[Const.ID], result=42)
```


### Cli

```
$ python3 rsq.py list_task
$ python3 rsq.py push --foo=bar 
61128c086f94b0d168e6a339
$ python3 rsq.py list_task
{'_id': ObjectId('61128c086f94b0d168e6a339'), 'state': 'todo', 'data': {'foo': 'bar'}}
$ python3 rsq.py pull -- -v # fire remove keys beginning with "_" hence the -v
_id: 61128c086f94b0d168e6a339
data: {"foo": "bar"}
$ python3 rsq.py done 61128c086f94b0d168e6a339 42
$ python3 rsq.py list_task
{'_id': ObjectId('61128c086f94b0d168e6a339'), 'state': 'done', 'data': {'foo': 'bar'}, 'result': 42}
```

## Install

```
pip install rsq
```
