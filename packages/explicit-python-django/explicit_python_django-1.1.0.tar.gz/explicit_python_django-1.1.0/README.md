# Explicit-Django
## Набор компонентов для интеграции Explicit с Django.

### Базовая единица работы на транзакциях Django ORM.

```python
# persons/core/unit_of_work.py

from explicit.django.unit_of_work import BaseUnitOfWork

from persons.core.persons.adapters.db import Repository as PersonsRepository
from persons.core.persons.adapters.db import repository as persons_repository

# (имя атрибута, инстанс репо)
KNOWN_REPOS = (
    ('persons', persons_repository),
)


class UnitOfWork(BaseUnitOfWork):

    persons: PersonsRepository

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registry.register(*KNOWN_REPOS)
```

### Декоратор для преобразования ошибок валидации предметной области в ошибки валидации Django
```python
from explicit.django.domain.validation.exceptions import handle_domain_validation_error

class ViewSet(...):

   @handle_domain_validation_error
   def create(self, request, *args, **kwargs):
       command = Command(...)
       bus.handle(command)

```
## Запуск тестов
```sh
$ tox
```
>>>>>>> e30984f (EDUEO-552 Вынос интеграции с django в отдельный пакет.)
