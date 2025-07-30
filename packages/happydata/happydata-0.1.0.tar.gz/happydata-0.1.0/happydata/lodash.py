from typing import List, Dict, Iterable, Generator, Callable,Any
import datetime,random,re,hashlib,hmac


def groupby(l: Iterable, key: str| Callable) -> Dict:
    """group a list by key
    @param l: list of dict
    @param key: key to group by
    @return: dict of key -> list of item
    """
    if not l:
        return {}
    if key and callable(key):
        d = {}
        for item in l:
            k = key(item)
            if k not in d:
                d[k] = []
            d[k].append(item)
        return d
    d = {}
    for item in l:
        k = item[key]
        if k not in d:
            d[k] = []
        d[k].append(item)
    return d

def indexby(l: Iterable, key: str| Callable , keep_first=True) -> Dict:
    """index a list by key
    @param l: list of dict
    @param key: key to index by
    @return: dict of key -> item
    """
    if not l:
        return {}
    if key and callable(key):
        d = {}
        for item in l:
            k = key(item)
            if k in d:
                if keep_first:
                    continue
            d[k] = item
        return d
    d = {}
    for item in l:
        k = item[key]
        if k in d:
            if keep_first:
                continue
        d[k] = item
    return d

def unique(l:List, fn:Callable=None,keep_first=True) -> List:
    """unique list and keep order"""
    if not l:
        return l
    d = {}
    r = []
    if fn:
        for item in l:
            k = fn(item)
            if k in d:
                if keep_first:
                    continue
            d[k] = True
            r.append(item)
        return r
    for item in l:
        if item in d:
            if keep_first:
                continue
        d[item] = True
        r.append(item)
    return r


def partition(l: Iterable,partition_size:int) -> Generator[List, None, None]:
    """Partition a list into partitions of size partition_size"""
    if l is None:
        return
    cur = []
    i = 0
    for v in l:
        cur.append(v)
        i += 1
        if i == partition_size:
            yield cur
            cur = []
            i = 0
    if cur:
        yield cur


def divide(l: List, num_partitions:int) -> List[List]:
    """Partition a list into num_partitions partitions"""
    if not l:
        return l
    partition_size = len(l)//num_partitions
    if partition_size == 0:
        partition_size = 1
    elif len(l) % num_partitions != 0:
        partition_size += 1
    return [l[i*partition_size : (i+1) * partition_size] for i in range (num_partitions)]

def flattern(l:List)->List:
    """flattern a list
    [1,[2,3],[4],[[2]]] -> [1,2,3,4 ,[2]]
    """
    if not l:
        return l
    return [x for i in l for x in (i if isinstance(i, list) or isinstance(i ,set) else [i])]

def flattern_deep(l:List)->List:
    """flattern a list deeply
    [1,[2,3],[4],[[2]]] -> [1,2,3,4 ,2]
    """
    if not l:
        return l
    return [x for i in l for x in (flattern_deep(i) if isinstance(i, list) or isinstance(i ,set) else [i])]

def index_of(l:List, v:Any|Callable)->int:
    """return the index of the first element , -1 not found """
    if callable(v):
        for i, e in enumerate(l):
            if v(e):
                return i
        return -1
    else:
        for i, e in enumerate(l):
            if e == v:
                return i
        return -1

def last_index_of(l:List, v:Any|Callable)->int:
    """return the index of the last element , -1 not found """
    if callable(v):
        for i, e in enumerate(reversed(l)):
            if v(e):
                return len(l) - i - 1
        return -1
    else:
        for i, e in enumerate(reversed(l)):
            if e == v:
                return len(l) - i - 1
        return -1


def now()->int:
    """return current time in seconds"""
    return int(datetime.datetime.now().timestamp())

def pick(d:Dict, keys:List)->Dict:
    """pick keys from a dict"""
    if not d or not keys:
        return d
    return {k: d[k] for k in keys if k in d}

def omit(d:Dict, keys:List)->Dict:
    """omit keys from a dict"""
    if not d or not keys:
        return d
    return {k: d[k] for k in d if k not in keys}

def compact(l:List)->List:
    """remove None, False, 0 from a list"""
    if not l:
        return l
    return [x for x in l if x]

def shuffle(l:List)->List:
    """shuffle a list"""
    l = [v for v in l]
    random.shuffle(l)
    return l

def sample(l:List, n:int)->List:
    """sample n elements from a list"""
    return random.sample(l, n)

def randstr(n:int, az=True,AZ=True, digits = True)->str:
    """generate a random string with length n"""
    s = ''
    if az:
        s += 'abcdefghijklmnopqrstuvwxyz'
    if AZ:
        s += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if digits:
        s += '0123456789'
    return ''.join(random.choices(s, k=n))

def rand(lower=0, upper=None)->int:
    """generate a random number between lower and upper"""
    if upper is None:
        upper = lower
        lower = 0
    return random.randint(lower, upper)

def clamp(n:int|float, lower:int|float, upper:int|float)->int|float:
    """clamp a number between lower and upper"""
    if lower > upper:
        lower, upper = upper, lower
    return max(lower, min(n, upper))


def union(*args:List)->List:
    """union multiple lists"""
    return list(set(flattern(args)))

def intersection(*args:List)->List:
    """intersection multiple lists"""
    return list(set.intersection(*map(set, args)))

def difference(a:List, b:List)->List:
    """difference of two lists"""
    return list(set(a) - set(b))

def argsort(l:List, key:Callable=None)->List:
    """sort a list by key and return the index"""
    if key:
        return sorted(range(len(l)), key=lambda i: key(l[i]))
    return sorted(range(len(l)), key=lambda i: l[i])

def trim_left(s:str, x:str=None)->str:
    """remove leading and trailing spaces"""
    if not x:
        return s.lstrip(x)
    if s.startswith(x):
        s =  s[len(x):]
        return trim_left(s, x)
    return s

def trim_right(s:str, x:str=None)->str:
    """remove trailing spaces"""
    if not x:
        return s.rstrip(x)
    if s.endswith(x):
        s =  s[:-len(x)]
        return trim_right(s, x)
    return s

def trim(s:str, x:str=None)->str:
    """remove leading and trailing"""
    return trim_left(trim_right(s, x), x)

def kv(**kwargs)->Dict:
    """create a new dict with non-None values"""
    return {k:v for k,v in kwargs.items() if v is not None}

def re_groups(s:str, pattern:str)->List[str]:
    """
    match a string with a regex pattern and return the group
    @param s: string
    @param pattern: regex pattern
    @param group: group index, None to return all groups
    @return: list of groups or group

    """
    if not s:
        return s
    m = re.match(pattern, s)
    if not m:
        return []
    return m.groups()

def re_find(s:str, pattern:str)->str:
    """
    match a string with a regex pattern and return the first match
    @param s: string
    @param pattern: regex pattern
    @return: first match
    """
    if not s:
        return s
    m = re.match(pattern, s)
    if not m:
        return ''
    return m.group(0)
    
def md5(s:str | bytes)->str:
    """md5 hash of a string"""
    if not s:
        return ''
    if isinstance(s, str):
        s = s.encode()
    return hashlib.md5(s).hexdigest()

def sha1(s:str | bytes)->str:
    """sha1 hash of a string or bytes"""
    if not s:
        return ''
    if isinstance(s, str):
        s = s.encode()
    return hashlib.sha1(s).hexdigest()

def sha256(s:str | bytes)->str:
    """sha256 hash of a string or bytes"""
    if not s:
        return ''
    if isinstance(s, str):
        s = s.encode()
    return hashlib.sha256(s).hexdigest()

def sha512(s:str | bytes)->str:
    """sha512 hash of a string or bytes"""
    if not s:
        return ''
    if isinstance(s, str):
        s = s.encode()
    return hashlib.sha512(s).hexdigest()

def hmac_sha256(s:str | bytes, key:str | bytes)->str:
    """hmac sha256 hash of a string or bytes"""
    if not s:
        return ''
    if isinstance(s, str):
        s = s.encode()
    if isinstance(key, str):
        key = key.encode()
    return hmac.new(key, s, hashlib.sha256).hexdigest()

def hmac_sha512(s:str | bytes, key:str | bytes)->str:
    """hmac sha512 hash of a string or bytes"""
    if not s:
        return ''
    if isinstance(s, str):
        s = s.encode()
    if isinstance(key, str):
        key = key.encode()
    return hmac.new(key, s, hashlib.sha512).hexdigest()