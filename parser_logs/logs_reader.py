def read_logs(filepath: str, chunk_size: int = int(1e6)) -> str:
    """Read big file

    Args:
        filepath (str): path to file
        chunk_size (int, optional): Chunk size of lines for reading. Defaults to 1e6.

    Returns:
        str: return chunksize strings

    Yields:
        Iterator[str]: [description]
    """
    with open(filepath) as file:
        data = []
        count = 0
        while True:
            line = file.readline()
            data.append(line)
            count += 1
            if not line:
                yield data
                del data
                break
            if count >= chunk_size:
                count = 0
                yield data
                del data
                data = []
