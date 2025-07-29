def write_file(path: str, content: str, encoding: str = 'utf-8', mode: str = 'w') -> None:
        with open(path, mode, encoding=encoding) as f:
            f.write(content)