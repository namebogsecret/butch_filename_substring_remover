# Batch Renamer

Batch Renamer - это скрипт для массового переименования файлов и папок в указанной директории. Он удаляет заданные подстроки из имен файлов и папок.

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/batch_renamer.git
   ```
2. Перейдите в директорию проекта:
   ```bash
   cd batch_renamer
   ```

## Использование

```bash
python batch_renamer.py /path/to/directory substring1 substring2 ...
```

Пример:
```bash
python batch_renamer.py /root/ test_1 test_2 test_3
```
```

### 4. setup.py
Этот файл используется для установки проекта через `pip`: