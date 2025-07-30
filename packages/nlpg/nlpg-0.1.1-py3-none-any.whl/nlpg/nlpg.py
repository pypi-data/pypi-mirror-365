#!/usr/bin/env python3
"""
Natural Language Password Generator.

Database source:
https://github.com/NaturalLanguagePasswords/system
"""

import itertools
import logging
import pathlib
import sqlite3
import types
import typing


class NaturalLanguagePassword:
    def __init__(self, self_random: bool = True) -> None:
        db_file = pathlib.Path(__file__).resolve().parent / "nlpg.db"
        self.log = logging.getLogger("nlp_gen")
        self.log.addHandler(logging.NullHandler())
        self._random = self_random
        self.log.debug("Initialise nlp.")
        if not db_file.exists():
            self.log.warning("Database not found.")
            self.db = sqlite3.connect(db_file)
            self._create(db_file.parent)
        else:
            self.db = sqlite3.connect(db_file)

    def __enter__(self):
        return self

    def __exit__(
        self,
        exctype: typing.Optional[typing.Type[BaseException]],
        excinst: typing.Optional[BaseException],
        exctb: typing.Optional[types.TracebackType],
    ) -> None:
        self.close()

    def _create(self, folder: pathlib.Path) -> None:
        self.log.info("First time DB generation...")
        sql_file = folder / "nlpg.sql"
        with self.db as database:
            for cmd in sql_file.read_text().split("\n"):
                database.execute(cmd)

    def add(self) -> None:
        raise NotImplementedError

    def remove(self) -> None:
        raise NotImplementedError

    def count_adj(self) -> int:
        cmd = "SELECT COUNT(*) FROM `word_list` WHERE adjective IS 1"
        return self.db.execute(cmd).fetchall()[0][0]

    def count_noun(self, plural: bool = False) -> int:
        cmd = "SELECT COUNT(*) FROM `word_list` WHERE noun IS 1"
        if not plural:
            cmd += "AND plural is 0"
        return self.db.execute(cmd).fetchall()[0][0]

    def get_adj(self) -> str:
        cmd = " ".join(
            [
                "SELECT `word` FROM `word_list`",
                "WHERE adjective IS 1",
                "ORDER BY random() LIMIT 1" if self._random else "",
            ],
        )
        self.log.debug(f"Executing: {cmd}")
        return self.db.execute(cmd).fetchone()[0]

    def get_noun(self, plural: bool = False) -> str:
        cmd = " ".join(
            [
                "SELECT `word` FROM `word_list`",
                "WHERE noun IS 1",
                "" if plural else "AND plural is 0",
                "ORDER BY random() LIMIT 1" if self._random else "",
            ],
        )
        self.log.debug(f"Executing: {cmd}")
        return self.db.execute(cmd).fetchone()[0]

    def close(self) -> None:
        self.db.close()


def get_password(pair_len: int = 3) -> str:
    """
    Get pair_len amount of Adjective & Noun pair back as string.

    Args:
        pair_len: The number of Adjective & Noun pairs.
    Returns:
        A string where the adjective & noun pairs are space separated.
    """
    with NaturalLanguagePassword() as nlp:
        return " ".join([
            f"{nlp.get_adj()} {nlp.get_noun()}"
            for _ in itertools.repeat(None, pair_len)
        ])
