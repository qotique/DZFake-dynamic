# DZFake-dynamic

A2S-прокси для подмены количества игроков в Steam A2S-ответах DayZ-сервера. Работает на **Linux** и **Windows**.

## Что делает

Слушает UDP-порт, проксирует запросы на реальный DayZ-сервер и добавляет фейковых игроков к A2S_INFO и A2S_PLAYER ответам. Количество фейковых игроков дрейфует в заданном диапазоне.

## Установка

### Из обфусцированного дистрибутива (рекомендуется)

1. Скачайте релиз или склонируйте репозиторий
2. Скопируйте `config.example.json` в `config.json` и настройте

### Сборка из исходников

```bash
pip install -r requirements.txt
bash build.sh       # Linux
python build.py     # Windows (альтернатива)
```

> **Кроссплатформенность:** Дистрибутив в `src/dist/` собирается под текущую ОС. Для Windows-сборки запустите `build.sh` на Windows (через WSL или Git Bash) или используйте `pyarmor gen` вручную. Полная кроссплатформенная сборка требует PyArmor Pro.

## Запуск

```bash
# Linux
python src/dist/a2s_proxy.py

# Windows
python src\dist\a2s_proxy.py

# С кастомным конфигом
python src/dist/a2s_proxy.py -c /path/to/config.json

# С аргументами командной строки (переопределяют конфиг)
python src/dist/a2s_proxy.py -p 27015 -t 2301 --min 5 --max 15
```

## Конфигурация

Скопируйте `config.example.json` в `config.json`:

```json
{
  "proxy_port": 2310,
  "real_port": 2311,
  "fake_players_min": 1,
  "fake_players_max": 3,
  "drift_interval_min": 300,
  "drift_interval_max": 600,
  "buffer_size": 4096,
  "timeout": 5.0
}
```

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `proxy_port` | Порт прокси (куда стучится Steam) | 2310 |
| `real_port` | Порт реального DayZ-сервера | 2311 |
| `fake_players_min` | Минимум фейковых игроков | 1 |
| `fake_players_max` | Максимум фейковых игроков | 3 |
| `drift_interval_min` | Мин. интервал дрейфа (сек) | 300 |
| `drift_interval_max` | Макс. интервал дрейфа (сек) | 600 |
| `buffer_size` | Размер буфера UDP | 4096 |
| `timeout` | Таймаут ответа (сек) | 5.0 |

CLI-аргументы (`-p`, `-t`, `--min`, `--max`) переопределяют значения из конфига.

## Настройка DayZ-сервера

В `serverDZ.cfg` укажите A2S-порт прокси (2310) вместо реального порта сервера. Steam будет стучаться на прокси, который проксирует на реальный сервер.

## Порядок портов

```
Steam Query  -->  :2310 (прокси)  -->  :2311 (DayZ сервер)
```

## Лицензия

MIT
