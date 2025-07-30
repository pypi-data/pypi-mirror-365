# Garpix Utils

Набор утилит для GARPIX CMS.

Утилиты:

* `file.get_file_path` - генерация пути для сохранения файла (для FileField)
* `string.get_random_string` - создание строки случайных символов
* `signature.make_signature_sha512` - создание цифровой подписи
* `models.ActiveMixin` - миксин для моделей, которым необходимо поле "Активность"
* `models.EmptyMixin` - миксин-пустышка, который можно использовать при обязательных миксинах
* `models.AvailableMixin` - миксин для моделей, которые должны обладать полями "Активность" и "Удалено"
* `models.PolymorphicActiveMixin` - миксин для модели `garpix_page.BasePage`, добавляет возможность выбора доступных страниц (которые активны). Используется внутри GARPIX CMS.
* `templatetags.url_replace` - подмена одного значения в dict на другое в Django-шаблонах.
* `models.DeleteMixin` - миксин для моделей, добавляющий функционал мягкого/жесткого удаления, `models.AdminDeleteMixin` - миксин для админ.модели.
* `models.PolymorphicAvailableMixin` - миксин для модели `garpix_page.BasePage`, добавляет возможность выбора доступных страниц (которые активны и неудалены). Используется внутри GARPIX CMS.
* `models.GarpixSiteConfiguration` - класс для добавления мультисайтовых настроек в проекте, `admin.GarpixSiteConfigurationAdmin` - класс для админ.панели


## Установка

Установка с помощью pip:

```bash
pip install garpix_utils
```

### Утилиты

#### `file.get_file_path` - генерация пути для сохранения файла (для FileField)
#### `file.get_secret_path` - генерация уникального пути для переданного имени файла

Формирует путь файла относительно года и месяца, чтобы множество файлов не скапливались на одном уровне.

Можно использовать в качестве значения 'upload_to' поля FileField модели Django. 

ПРИМЕР:

```
from garpix_utils.file import get_file_path
from django.db import models


class FileModel(models.Model):
    # ...
    file = models.FileField(upload_to=get_file_path, blank=True, null=True, verbose_name=_('File'))
    # ...
```


#### `string.get_random_string` - создание строки случайных символов

Создает случайную строку указанного размера и с указанными символами.

Параметры:

* size: int - количество символов. По умолчанию - 8.
* chars: str - строка из списка символов, которые могут быть в строке. По умолчанию `string.ascii_uppercase + string.digits`.

ПРИМЕР:

Пример 1

```
from garpix_utils.string import get_random_string

random_string = get_random_string(16)

# random_string = '451DNCLZLY2HDDDX'
```

Пример 2

```
import string
from garpix_utils.string import get_random_string

random_string = get_random_string(8, string.ascii_lowercase)

# random_string = 'palsjpyz'
```

Пример 3

```
from garpix_utils.string import get_random_string

random_string = get_random_string(16, '01')

# random_string = '0110111101010100'
```

#### `signature.make_signature_sha512` - создание цифровой подписи

Создает сигнатуру (цифровую подпись) по указанным параметрам с хэшированием SHA-512.

Обычно используется для эквайринга в качестве защиты цифровой подписью.

ВНИМАНИЕ! Если необходим другой алгоритм шифрования, то загляните в эту функцию, можно сделать свой по аналогии.

Параметры:

* params: dict - словарь параметров. Если присутствует signature_key, то он будет удален.
* signature_key: str - ключ параметра с сигнатурой. По умолчанию "sig".
* secret: str - секретный ключ, который будет приконкатенирован в конце перед хэшированием.

Алгоритм:

1. Берет словарь параметров, удаляет оттуда параметр с ключом сигнатуры (см. переменную signature_key, по умолчанию значение "sig")
2. Получившийся словарь сортирует по названию ключа в алфавитном порядке. Все вложенные данные тоже сортируются по ключу, списочные - просто по алфавиту.
3. Последовательно конкатенирует ключ со значением в единую строку.
4. В конце конкатенирует значение переменной secret (по умолчанию равна "secret").
5. Хэширует по алгоритму SHA-512 и возвращает строку в нижнем регистре.
6. Возвращает получившийся результат.

ПРИМЕР:

```python
# необходимый вам файл

from garpix_utils.signature import make_signature_sha512


sig = make_signature_sha512({'a': 'xxx', 'c': 'ggg', 'b': '111', 'sig': '123', 'd': [3, 1, 2], 'e': {'b': '2', 'a': '1'}}, signature_key='sig', secret='secret')

# sig = '2123086085ec1fe67595d7b3d2b6a0dbf3f33e528d78366b8d62d7f0a7e3c090077b0f7b8dc84921a6087aa57b8284bd1e74702df7a16e96f73f627e6eea815a'
```

Разбор примера по шагам:

**Шаг 1**

* Было: {'a': 'xxx', 'c': 'ggg', 'b': '111', 'sig': '123', 'd': [3, 1, 2], 'e': {'b': '2', 'a': '1'}}
* Стало: {'a': 'xxx', 'c': 'ggg', 'b': '111', 'd': [3, 1, 2], 'e': {'b': '2', 'a': '1'}}

**Шаг 2**

* Было: {'a': 'xxx', 'c': 'ggg', 'b': '111', 'd': [3, 1, 2], 'e': {'b': '2', 'a': '1'}}
* Стало: {'a': 'xxx', 'b': '111', 'c': 'ggg', 'd': [1, 2, 3], 'e': {'a': '1', 'b': '2'}}

**Шаг 3**

* Было: {'a': 'xxx', 'b': '111', 'c': 'ggg', 'd': [1, 2, 3], 'e': {'a': '1', 'b': '2'}}
* Стало: 'axxxb111cgggd123ea1b2'

**Шаг 4**

* Было: 'axxxb111cgggd123ea1b2'
* Стало: 'axxxb111cgggd123ea1b2secret'

**Шаг 5**

* Было: 'axxxb111cgggd123ea1b2secret'
* Стало: '2123086085ec1fe67595d7b3d2b6a0dbf3f33e528d78366b8d62d7f0a7e3c090077b0f7b8dc84921a6087aa57b8284bd1e74702df7a16e96f73f627e6eea815a'

#### `models.ActiveMixin` - миксин для моделей, которым необходимо поле "Активность"

Добавляет поле `is_active (Boolean, default=True)`. Добавляет менеджера `active_objects`, который выбирает только активные объекты (`is_active=True`).

ПРИМЕР:

```python
# необходимый вам файл

from django.db import models
from garpix_utils.models import ActiveMixin


class Product(ActiveMixin, models.Model):
    pass


Product.active_objects.all()

# Будут выбраны записи только с is_active == True.
```

#### `models.EmptyMixin` - миксин-пустышка, который можно использовать при обязательных миксинах

ПРИМЕР:

```python
# необходимый вам файл

from django.db import models
from garpix_utils.models import EmptyMixin


class Product(EmptyMixin, models.Model):
    pass

# Ничего не изменилось.
```

Или использование в пакете `garpix_blog`:

```python
# app/settings.py

GARPIX_BLOG_MIXIN = 'garpix_utils.models.EmptyMixin'

```

#### `models.AvailableMixin` - миксин для моделей, которые должны обладать полями "Активность" и "Удалено"

Добавляет поля `is_active (Boolean, default=True)` и `is_deleted (Boolean, default=False)`. Добавляет менеджера `available_objects`, который выбирает только доступные объекты (`is_active=True, is_deleted=False`).

ПРИМЕР:

```python
# необходимый вам файл

from django.db import models
from garpix_utils.models import AvailableMixin


class Product(AvailableMixin, models.Model):
    pass


Product.available_objects.all()

# Будут выбраны записи только с is_active == True.
```

#### `templatetags.url_replace` - подмена одного значения в dict на другое в Django-шаблонах.

ПРИМЕР для пагинации (взято из https://github.com/garpixcms/garpix_page/):

```
{% load url_replace %}

<nav>
    <ul class="pagination">
        {% for page_num in page_range %}
            <li class="page-item {% if page_num == page %}active{% endif %}">
                <a class="page-link" href="?{% url_replace request 'page' page_num %}">{{ page_num }}</a>
            </li>
        {% endfor %}
    </ul>
</nav>
```

# Changelog

See [CHANGELOG.md](CHANGELOG.md).

# Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

# License

[MIT](LICENSE)