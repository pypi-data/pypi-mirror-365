"""Реализация "Единицы работы"."""
from django.db import transaction

from explicit.unit_of_work import AbstractTransactionStrategy
from explicit.unit_of_work import AbstractUnitOfWork


class BaseUnitOfWork(AbstractUnitOfWork):

    """Реализация единицы работы для использования совместно с Django ORM."""

    savepoint: bool
    strategy: 'AbstractTransactionStrategy'

    def __init__(self, *, savepoint: bool = False) -> None:
        super().__init__()
        assert isinstance(savepoint, bool), savepoint
        self.savepoint = savepoint

    def _get_new_self(self) -> 'AbstractUnitOfWork':
        return type(self)(savepoint=True)

    def __enter__(self) -> 'AbstractUnitOfWork':
        if self.savepoint:
            self.strategy = SavepointTransactionStrategy()
        else:
            self.strategy = TransactionStrategy()
        return super().__enter__()


class TransactionStrategy(AbstractTransactionStrategy):

    """Стандартная транзакционная стратегия."""

    def __enter__(self):
        transaction.set_autocommit(False)

    def __exit__(self, *_):
        transaction.set_autocommit(True)

    def commit(self):
        """Зафиксировать транзакцию."""
        transaction.commit()

    def rollback(self):
        """Откатить транзакцию."""
        transaction.rollback()


class SavepointTransactionStrategy(AbstractTransactionStrategy):

    """Транзакционная стратегия на точках сохранения."""

    savepoint_id: str

    def __init__(self) -> None:
        savepoint_id = transaction.savepoint()
        assert isinstance(savepoint_id, str), savepoint_id
        self.savepoint_id = savepoint_id

    def commit(self):
        """Зафиксировать транзакцию."""
        transaction.savepoint_commit(self.savepoint_id)

    def rollback(self):
        """Откатить транзакцию."""
        transaction.savepoint_rollback(self.savepoint_id)
