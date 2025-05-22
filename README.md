# Cosmos Wallet Automation 🚀

Автоматизированная система для управления кошельками Cosmos Hub с интеллектуальным расчетом газа и распределением средств на биржи.

## ✨ Возможности

- 🤖 **Автоматическое снятие стейкинг-наград** с валидаторов
- 💸 **Отправка средств на биржи** (OKX, Bitget)
- ⚡ **Динамический расчет газа** на основе анализа блокчейна
- 🔄 **Отказоустойчивость** с множественными RPC узлами
- 📊 **Детальная статистика** и мониторинг операций
- 🎨 **Красивый интерфейс** с цветным выводом

## 🏗️ Архитектура проекта

```
cosm/
├── 🐍 Python Core
│   ├── script.py                    # Основной скрипт автоматизации
│   ├── config.py                    # Конфигурация системы
│   └── logger.py                    # Система логирования
├── 🔧 Shell Scripts
│   ├── calculate_gas.sh             # Расчет газа для снятия наград
│   ├── calculate_send_gas.sh        # Расчет газа для отправки
│   └── calculate_mantra_gas.sh      # Расчет газа для Mantra Chain
├── 🟡 JavaScript Modules
│   ├── gas-calculator.js            # Современный расчет газа (CosmJS)
│   ├── rpc-client.js               # Клиент для работы с RPC
│   ├── monitoring.js               # Мониторинг и алерты
│   └── health-check.js             # Проверка состояния RPC узлов
├── 📁 Data
│   ├── okx_wallets                 # Адреса кошельков OKX
│   ├── bitget_wallets              # Адреса кошельков Bitget
│   └── logs/                       # Логи операций
├── 📄 Configuration
│   ├── package.json                # JS зависимости
│   ├── requirements.txt            # Python зависимости
│   └── .env.example               # Пример переменных окружения
└── 📚 Documentation
    ├── README.md                   # Документация
    └── SETUP.md                   # Инструкция по настройке
```

## 📋 Системные требования

### Обязательные компоненты:
- **Python 3.8+** с pip
- **Node.js 16+** с npm
- **Cosmos SDK CLI** (`gaiad`)
- **jq** для обработки JSON
- **Операционная система**: Linux/macOS (рекомендуется Ubuntu 20.04+)

### Python зависимости:
```bash
colorama>=0.4.4
requests>=2.28.0
```

### JavaScript зависимости:
```bash
@cosmjs/stargate@^0.32.4
@cosmjs/tendermint-rpc@^0.32.4
axios@^1.6.0
chalk@^4.1.2
winston@^3.11.0
```

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
# Клонируем репозиторий
git clone https://github.com/zukaman/cosm.git
cd cosm

# Устанавливаем Python зависимости
pip install -r requirements.txt

# Устанавливаем Node.js зависимости
npm install

# Делаем скрипты исполняемыми
chmod +x *.sh
```

### 2. Подготовка файлов кошельков

Создайте два файла с адресами кошельков бирж:

#### `okx_wallets` (один адрес на строку):
```
cosmos1abc123...def456
cosmos1ghi789...jkl012
cosmos1mno345...pqr678
...
```

#### `bitget_wallets` (один адрес на строку):
```
cosmos1stu901...vwx234
cosmos1yza567...bcd890
cosmos1efg123...hij456
...
```

**⚠️ Важно:**
- Каждый файл должен содержать **минимум 119 адресов**
- Адреса должны быть валидными Cosmos адресами (начинаются с `cosmos1`)
- Один адрес на строку, без пустых строк
- Используйте адреса **депозита** с ваших бирж

### 3. Настройка Cosmos CLI

```bash
# Проверяем установку gaiad
gaiad version

# Добавляем ваши кошельки в keyring
gaiad keys add Wallet1 --recover
gaiad keys add Wallet2 --recover
# ... добавьте все 119 кошельков
```

### 4. Конфигурация

Отредактируйте `config.py` под ваши нужды:

```python
# Основные параметры
GAS_PRICE = 0.005              # Цена газа
NUM_WALLETS = 119              # Количество кошельков

# Пороги операций
MIN_REWARDS_TO_WITHDRAW = 700000   # Минимум наград (0.7 ATOM)
MIN_SEND_AMOUNT = 50000           # Минимум для отправки (0.05 ATOM)

# Задержки между операциями
MIN_DELAY = 3600              # 1 час
MAX_DELAY = 7200              # 2 часа
```

## 🎮 Запуск системы

### Основной режим:
```bash
python script.py
```

### Тестирование расчета газа:
```bash
# Проверка расчета газа для снятия наград
./calculate_gas.sh

# Проверка расчета газа для отправки
./calculate_send_gas.sh

# Современный JS расчет газа
npm run gas-withdraw
npm run gas-send
```

### Мониторинг системы:
```bash
# Проверка состояния RPC узлов
npm run health-check

# Запуск мониторинга
npm run monitor
```

## 📊 Логика работы

### Последовательность операций для каждого кошелька:

1. **📊 Анализ баланса** - проверка текущего состояния
2. **⛽ Расчет газа** - динамический анализ сети
3. **🎁 Снятие наград** - если > 0.7 ATOM
4. **💸 Отправка средств** - оставляя 15-25k uatom
5. **⏳ Задержка** - 1-2 часа до следующего кошелька

### Умная обработка ошибок:

- **Out of gas** → увеличение лимита газа на 20%
- **RPC недоступен** → переключение на другой узел
- **Ошибка транзакции** → до 3 попыток с экспоненциальной задержкой

## 🔧 Расширенные возможности

### Переменные окружения (.env):
```bash
# Webhook для уведомлений
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Кастомные RPC узлы
CUSTOM_RPC_1=https://your-rpc-1.com
CUSTOM_RPC_2=https://your-rpc-2.com

# Режим отладки
DEBUG_MODE=true
DRY_RUN=false
```

### Кастомизация конфигурации:

```python
# Добавление новых бирж
EXCHANGE_WALLETS = {
    'okx': 'okx_wallets',
    'bitget': 'bitget_wallets',
    'binance': 'binance_wallets'  # Новая биржа
}

# Настройка газа для разных операций
GAS_SETTINGS = {
    'withdraw_single': 180000,
    'withdraw_multiple': 350000,
    'send_simple': 120000,
    'send_complex': 250000
}
```

## 📈 Мониторинг и статистика

### Файлы логов:
- `logs/cosmos_YYYYMMDD.log` - основные операции
- `logs/errors_YYYYMMDD.log` - ошибки и предупреждения
- `logs/stats_YYYYMMDD.json` - статистика за день

### Пример статистики:
```json
{
  "date": "2024-05-22",
  "processed_wallets": 119,
  "successful_withdrawals": 87,
  "total_rewards_withdrawn": "245.67 ATOM",
  "total_amount_sent": "1,234.56 ATOM",
  "success_rate": "94.2%",
  "average_gas_used": 185432
}
```

## 🛠️ Устранение неполадок

### Частые проблемы:

**1. Ошибка "gaiad: command not found"**
```bash
# Установите Cosmos SDK
wget https://github.com/cosmos/gaia/releases/latest/download/gaiad-linux-amd64
sudo mv gaiad-linux-amd64 /usr/local/bin/gaiad
sudo chmod +x /usr/local/bin/gaiad
```

**2. Ошибка "insufficient funds"**
- Проверьте баланс кошельков
- Убедитесь, что есть средства для комиссий
- Снизите `MIN_SEND_AMOUNT` в конфигурации

**3. Ошибки RPC соединения**
- Проверьте интернет соединение
- Запустите `npm run health-check`
- Добавьте альтернативные RPC в конфигурацию

**4. Проблемы с keyring**
```bash
# Проверьте доступность кошельков
gaiad keys list

# Убедитесь, что все 119 кошельков добавлены
for i in {1..119}; do
  gaiad keys show Wallet$i -a || echo "Wallet$i не найден"
done
```

## 🔒 Безопасность

### Рекомендации:

1. **🔐 Приватные ключи** - храните в безопасном месте
2. **🌐 VPN** - используйте при работе с кошельками
3. **📱 2FA** - включите на всех биржах
4. **💾 Бэкапы** - регулярно создавайте копии keyring
5. **📊 Мониторинг** - следите за логами операций

### Лимиты безопасности:
- Максимум 3 попытки для каждой операции
- Случайные задержки для защиты от детекции
- Автоматическая остановка при критических ошибках

## 🤝 Поддержка

### Получить помощь:
- 📧 Email: [создать issue в GitHub]
- 📱 Telegram: [@zukaman]
- 🐛 Баги: [GitHub Issues](https://github.com/zukaman/cosm/issues)

### Внести вклад:
1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - свободно используйте для своих проектов.

---

**⚠️ Дисклеймер:** Используйте на свой страх и риск. Авторы не несут ответственности за потерю средств. Всегда тестируйте на небольших суммах перед полным запуском.

**💡 Совет:** Начните с тестового режима (`DRY_RUN=true`) для изучения работы системы без реальных транзакций.