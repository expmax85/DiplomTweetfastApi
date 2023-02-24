import os
import aiofiles


async def write_to_disk(content: bytes, file_path: str) -> None:
    async with aiofiles.open(file_path, mode='wb') as f:
        await f.write(content)


async def remove_files_from_disk(del_list: list) -> None:
    for path in del_list:
        os.remove(str(path))
