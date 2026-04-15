from __future__ import annotations

import pytest

from DataGen import main_iris


class FakeSQLError(Exception):
    def __init__(self, sqlcode: int, message: str = "") -> None:
        super().__init__(message)
        self.sqlcode = sqlcode


class FakeStatement:
    def __init__(self, error: Exception | None = None) -> None:
        self._error = error
        self.executed = False

    def execute(self, *args) -> None:
        if self._error is not None:
            raise self._error
        self.executed = True


class FakeSQL:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.prepared_sql: list[str] = []

    def prepare(self, sql: str) -> FakeStatement:
        self.prepared_sql.append(sql)
        return FakeStatement(self.error)


class FakeIris:
    def __init__(self, error: Exception | None = None) -> None:
        self.sql = FakeSQL(error)


def test_exec_sql_ignores_empty_delete_sqlcode_100() -> None:
    iris = FakeIris(FakeSQLError(100))

    main_iris._exec_sql(iris, "DELETE FROM Finance.Disputes")

    assert iris.sql.prepared_sql == ["DELETE FROM Finance.Disputes"]


def test_exec_sql_keeps_other_sql_errors() -> None:
    iris = FakeIris(FakeSQLError(-29, "table not found"))

    with pytest.raises(RuntimeError, match="DELETE FROM Finance.Disputes"):
        main_iris._exec_sql(iris, "DELETE FROM Finance.Disputes")