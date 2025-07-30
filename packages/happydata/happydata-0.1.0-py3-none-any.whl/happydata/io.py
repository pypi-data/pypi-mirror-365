import json,os,gzip,io,tarfile,zipfile
from typing import List,Dict,Iterable,Generator,Optional,IO,Tuple,BinaryIO,Any
from pathlib import Path

def write_jsonl(l: Iterable, to:str , append:bool=False):
    """write a list of dict to a jsonl file, support both .gz and plain text"""
    if str(to).endswith('.gz'):
        write_jsonl_gz(l, to, append=append)
        return
    with open(to, 'a' if append else 'w') as f:
        for item in l:
            f.write(json.dumps(item, ensure_ascii=False, default=vars) + '\n')

def read_jsonl(from_file:str |Path| IO)->Generator[Any,str,None]:
    """read a jsonl file as a json object generator, support both .gz and plain text"""
    if isinstance(from_file, str) or isinstance(from_file, Path):
        if str(from_file).endswith('.gz'):
            with gzip.open(from_file, 'rt') as f:
                for line in f:
                    yield json.loads(line)
        else:
            with open(from_file, 'r') as f:
                for line in f:
                    yield json.loads(line)
    else:
        for line in from_file:
            yield json.loads(line)

def write_jsonl_gz(l: Iterable, to:str, add_end=True, append:bool=False):
    """write a list of dict to a jsonl file"""
    with gzip.open(to, 'at' if append else 'wt') as f:
        for item in l:
            if add_end:
                f.write(json.dumps(item, ensure_ascii=False, default=vars) + '\n')
            else:
                f.write(json.dumps(item, ensure_ascii=False, default=vars))

def read_jsonl_gz(from_file:str|Path| IO)->Generator[Any,str,None]:
    """read a jsonl file as a json object generator"""
    if isinstance(from_file, str) or isinstance(from_file, Path):
        with gzip.open(from_file, 'rt') as f:
            for line in f:
                yield json.loads(line)
    else:
        for line in from_file:
            yield json.loads(line)

def load_jsonl(from_file:str)->List[Any]:
    """load a jsonl file to memory as a list of json object, support both .gz and plain text"""
    return list(read_jsonl(from_file))

def load_jsonl_gz(from_file:str)->List[Dict]:
    """load a jsonl file to memory as a list of json object"""
    return list(read_jsonl_gz(from_file))

def load_lines(file:str, remove_end=True)->List[str]:
    """load a text file to memory as a list of string, support both .gz and plain text"""
    return list(read_lines(file , remove_end))

def read_lines(file:str|Path,remove_end=True)->Generator[str,str,None]:
    """read a text file as a line generator, remove \n and \r by default. support both .gz and plain text"""
    if str(file).endswith('.gz'):
        with gzip.open(file, 'rt') as f:
            for line in f:
                if remove_end:
                    yield line.removesuffix('\n').removesuffix('\r')
                else:
                    yield line
    else:
        with open(file, 'r') as f:
            for line in f:
                if remove_end:
                    yield line.removesuffix('\n').removesuffix('\r')
                else:
                    yield line

def read_lines_gz(file:str,remove_end=True)->Generator[str,str,None]:
    """read a text file as a line generator, remove \n and \r by default"""
    with gzip.open(file, 'rt') as f:
        for line in f:
            if remove_end:
                yield line.removesuffix('\n').removesuffix('\r')
            else:
                yield line

def write_lines(lines:Iterable[str],to:str|Path ,add_end=True, append:bool=False):
    """write a list of string to a text file, support both .gz and plain text"""
    if str(to).endswith('.gz'):
        write_lines_gz(lines, to, add_end, append)
        return
    with open(to, 'a' if append else 'w') as f:
        for line in lines:
            if add_end:
                f.write(str(line)+'\n')
            else:
                f.write(str(line))
def write_lines_gz(lines:Iterable[str],to:str|Path ,add_end=True, append:bool=False):
    with gzip.open(to, 'at' if append else 'wt') as f:
        for line in lines:
            if add_end:
                f.write(str(line)+'\n')
            else:
                f.write(str(line))

def read_tar_gz(file:str|Path) -> Generator[Tuple[tarfile.TarInfo,IO],str,None]:
    """read a tar.gz file as a file generator"""
    with tarfile.open(file, 'r:gz') as tar:
        for member in tar.getmembers():
            with tar.extractfile(member) as f:
                yield member , f

def write_tar_gz(file:str|Path,files:Dict[str,BinaryIO]):
    """write a dict of file to a tar.gz file"""
    with tarfile.open(file, 'w:gz') as tar:
        for name, f in files.items():
            info = tarfile.TarInfo(name)
            buf = f.read()
            info.size = len(buf)
            tar.addfile(info, io.BytesIO(buf))

def read_zip(file:str|Path) -> Generator[Tuple[str,IO],str,None]:
    """read a zip file as a file generator"""
    with zipfile.ZipFile(file, 'r') as z:
        for member in z.namelist():
            with z.open(member) as f:
                yield member , f

def write_zip(file:str|Path,files:Dict[str,BinaryIO]):
    """write a dict of file to a zip file"""
    with zipfile.ZipFile(file, 'w') as z:
        for name, f in files.items():
            z.writestr(name, f.read())

def load_text(file:str|Path)->str:
    """file to text"""
    if str(file).endswith('.gz'):
        with gzip.open(file, 'rt') as f:
            return f.read()
    with open(file, 'r') as f:
        return f.read()

def write_text(s:str,to:str|Path, append:bool=False):
    """text to file"""
    if str(to).endswith('.gz'):
        with gzip.open(to, 'at' if append else 'wt') as f:
            f.write(s)
        return
    with open(to, 'a' if append else 'w') as f:
        f.write(s)

def load_json(file:str|Path)->Dict:
    """file to json"""
    if str(file).endswith('.gz'):
        with gzip.open(file, 'rt') as f:
            return json.load(f)
    with open(file, 'r') as f:
        return json.load(f)

def write_json(d:Dict,to:str|Path):
    """json to file"""
    if str(to).endswith('.gz'):
        with gzip.open(to, 'wt') as f:
            json.dump(d, f,ensure_ascii=False, default=vars)
        return
    with open(to, 'w') as f:
        json.dump(d, f,ensure_ascii=False, default=vars)

def match_suffix(file:str|Path,suffix:str|List)->bool:
    """check if a file has a suffix"""
    if isinstance(suffix, str):
        return str(file).lower().endswith(suffix.lower())
    if isinstance(suffix, list):
        for s in suffix:
            if str(file).lower().endswith(s.lower()):
                return True
        return False

def read_dir(d:str|Path, recursive:bool=False,suffix:str|List=None)->Generator[str,str,None]:
    """list all files in a directory in absolute path"""
    if not recursive:
        for f in os.listdir(d):
            if suffix:
                if os.path.isfile(os.path.join(d,f)) and match_suffix(f, suffix):
                    yield os.path.abspath(os.path.join(d,f))
            else:
                if os.path.isfile(os.path.join(d,f)):
                    yield os.path.abspath(os.path.join(d,f))
    else:
        for root, dirs, files in os.walk(d):
            for f in files:
                if suffix:
                    if match_suffix(f, suffix):
                        yield os.path.abspath(os.path.join(root,f))
                else:
                    yield os.path.abspath(os.path.join(root,f))

def load_dir(d:str|Path, recursive:bool=False,suffix:str=None)->List[str]:
    """list all files in a directory in absolute path"""
    return list(read_dir(d, recursive, suffix))


def read_tar(file:str|Path) -> Generator[Tuple[tarfile.TarInfo,IO],str,None]:
    """read a tar file as a file generator"""
    with tarfile.open(file, 'r') as tar:
        for member in tar.getmembers():
            with tar.extractfile(member) as f:
                yield member , f

def write_tar(file:str|Path,files:Dict[str,BinaryIO]):
    """write a dict of file to a tar file"""
    with tarfile.open(file, 'w') as tar:
        for name, f in files.items():
            info = tarfile.TarInfo(name)
            buf = f.read()
            info.size = len(buf)
            tar.addfile(info, io.BytesIO(buf))