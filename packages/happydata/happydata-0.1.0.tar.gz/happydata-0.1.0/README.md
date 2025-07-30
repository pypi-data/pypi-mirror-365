# happydata
happy data loading,writing, transforming without third party library



## Installation
```bash
pip install happydata
```

## Usage
```python
from happydata import *
import io

class User:
    def __init__(self, name:str, age:int):
        self.name = name
        self.age = age
tmp_path = 'test_users.jsonl'
# jsonl
write_jsonl([User('name', 18), User('张三', 19)], tmp_path)
assert load_jsonl(tmp_path) == [{'name': 'name', 'age': 18}, {'name': '张三', 'age': 19}]

# jsonl.gz
records = load_jsonl_gz('test_users.jsonl.gz')
write_jsonl_gz(records, 'test_users.jsonl.gz')
# lines
for line in read_lines('test_users.jsonl'):
    print(line)
write_lines(lines, 'test_users.jsonl')

# tar.gz
for item, f in read_tar_gz(tmp_path):
    print(item.name)
    bs= f.read()
write_tar_gz(records, {
    'test.txt': io.BytesIO(b'hello'),
    }, 'test.tar.gz')

# zip
for name, f in read_zip(tmp_path):
    print(name)
    bs = f.read()
write_zip({
    'test.txt': io.BytesIO(b'hello'),
    }, 'test.zip')

# dir
files = load_dir('test_dir')

# commands:
state,stdout,stderr = run('ls')

# transform:
groupby([{'name': 'name', 'age': 18}, {'name': '张三', 'age': 19}], 'name')

```