"""Mucking about with data download."""

import asyncio
import enum
import shutil
from asyncio import AbstractEventLoop
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from zipfile import ZipFile

import aiofile
import httpx


# async def download()

# import requests, zipfile, io
# r = requests.get(zip_file_url)
# z = zipfile.ZipFile(io.BytesIO(r.content))
# z.extractall("/path/to/destination_directory")

# def loop_dfs(dfs):  # note: ordinary def
#     def clean_df(df):
#         ...
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = [executor.submit(clean_df, df)
#                    for (table, df) in dfs.items()]
#         concurrent.futures.wait(futures)

# https://www.ssa.gov/oact/babynames/names.zip
# https://www.ssa.gov/oact/babynames/state/namesbystate.zip
# https://www.ssa.gov/oact/babynames/territory/namesbyterritory.zip


class NameURL(enum.Enum):
    US = "https://www.ssa.gov/oact/babynames/names.zip"
    states = "https://www.ssa.gov/oact/babynames/state/namesbystate.zip"
    territories = "https://www.ssa.gov/oact/babynames/territory/namesbyterritory.zip"


class DataStore:
    data_dir: Path
    process_pool: ProcessPoolExecutor
    loop: AbstractEventLoop

    async def get_zips(self, force: bool = False) -> None:
        await asyncio.gather(
            *[
                asyncio.create_task(self.get_zip(source, force=force))
                for source in list(NameURL)
            ]
        )

    async def get_zip(self, source: NameURL = NameURL.US, force: bool = False) -> None:
        zip_path = self.data_dir / Path(source.value).name
        if not zip_path.exists() or force:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(source.value)
            response.raise_for_status()
            async with aiofile.async_open(zip_path, "wb") as f:
                await f.write(response.content)
            await self.loop.run_in_executor(
                self.process_pool, partial(self.unzip, zip_path)
            )

    def unzip(self, zip_path: Path) -> None:
        unzip_dir = self.data_dir / zip_path.name
        if unzip_dir.exists():
            shutil.rmtree(str(unzip_dir))
        unzip_dir.mkdir(parents=True)
        with ZipFile(zip_path) as z:
            z.extractall(unzip_dir)
