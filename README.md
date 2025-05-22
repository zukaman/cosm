# 🚀 Cosmos Wallet Automation - ПОЛНАЯ НАСТРОЙКА ЗАВЕРШЕНА!

## 📁 Итоговая структура проекта

```
cosm/
├── 🐍 Python Core
│   ├── script.py                    # Основной скрипт автоматизации
│   ├── config.py                    # Система конфигурации  
│   └── logger.py                    # Продвинутое логирование
├── 🔧 Shell Scripts  
│   ├── calculate_gas.sh             # Расчет газа для снятия наград
│   ├── calculate_send_gas.sh        # Расчет газа для отправки
│   ├── calculate_mantra_gas.sh      # Расчет газа для Mantra Chain
│   └── start.sh                     # Интерактивный стартовый скрипт
├── 🟡 JavaScript Modules
│   ├── gas-calculator.js            # Современный расчет газа (CosmJS)
│   ├── rpc-client.js               # Умный клиент для RPC
│   ├── monitoring.js               # Мониторинг и уведомления  
│   └── health-check.js             # Проверка состояния системы
├── 📁 Configuration Files
│   ├── package.json                # JS зависимости
│   ├── requirements.txt            # Python зависимости
│   ├── .env.example               # Шаблон переменных окружения
│   ├── config.py                  # Основная конфигурация
│   ├── okx_wallets.example        # Пример адресов OKX
│   └── bitget_wallets.example     # Пример адресов Bitget
├── 📚 Documentation
│   ├── README.md                  # Подробная документация
│   └── SETUP.md                   # Быстрый старт
└── 📊 Runtime (создается автоматически)
    ├── logs/                      # Логи операций
    ├── okx_wallets               # Ваши адреса OKX
    └── bitget_wallets            # Ваши адреса Bitget
```

## 🎯 БЫСТРЫЙ ЗАПУСК

### 1️⃣ Клонирование и установка
```bash
git clone https://github.com/zukaman/cosm.git
cd cosm

# Делаем скрипты исполняемыми
chmod +x *.sh
chmod +x start.sh

# Запускаем интерактивную настройку
./start.sh
```

### 2️⃣ Подготовка файлов кошельков

**Создайте файл `okx_wallets`:**
```bash
cp okx_wallets.example okx_wallets
# Отредактируйте файл, добавив 119+ реальных адресов OKX
nano okx_wallets
```

**Создайте файл `bitget_wallets`:**
```bash
cp bitget_wallets.example bitget_wallets  
# Отредактируйте файл, добавив 119+ реальных адресов Bitget
nano bitget_wallets
```

**Формат файлов кошельков:**
```
cosmos1abc123def456ghi789jkl012mno345pqr678stu901
cosmos1vwx234yza567bcd890efg123hij456klm789nop012
cosmos1qrs345tuv678wxy901zab234cde567fgh890ijk123
# ... еще 116+ адресов
```

### 3️⃣ Добавление кошельков в gaiad
```bash
# Добавляем все 119 кошельков
for i in {1..119}; do
  gaiad keys add Wallet$i --recover
done

# Проверяем
gaiad keys list | wc -l  # Должно быть 119
```

### 4️⃣ Настройка конфигурации (опционально)
```bash
cp .env.example .env
nano .env  # Настройте под свои нужды
```

## 🚀 СПОСОБЫ ЗАПУСКА

### Интерактивный запуск (рекомендуется)
```bash
./start.sh
```
Скрипт автоматически:
- ✅ Проверит все зависимости
- ✅ Проверит состояние RPC узлов  
- ✅ Подсчитает кошельки
- ✅ Предложит варианты запуска

### Прямой запуск Python
```bash
# Тестовый режим
DRY_RUN=true python3 script.py

# Рабочий режим  
DRY_RUN=false python3 script.py
```

### Использование JavaScript модулей
```bash
# Проверка RPC узлов
npm run health-check

# Тест расчета газа
npm run gas-withdraw
npm run gas-send

# Мониторинг системы
npm run monitor
```

## 🛠️ ПОЛЕЗНЫЕ КОМАНДЫ

### Проверка системы
```bash
# Проверка всех компонентов
./start.sh

# Проверка конфигурации  
python3 -c "from config import get_config_summary; print(get_config_summary())"

# Проверка кошельков
for i in {1..5}; do
  echo "Wallet$i: $(gaiad keys show Wallet$i -a)"
done
```

### Мониторинг в реальном времени
```bash
# Логи основного скрипта
tail -f logs/cosmos_$(date +%Y%m%d).log

# Статистика за сегодня
cat logs/stats_$(date +%Y%m%d).json | jq '.'

# Проверка состояния RPC
npm run health-check
```

### Тестирование
```bash
# Тест расчета газа (bash)
./calculate_gas.sh
./calculate_send_gas.sh

# Тест расчета газа (JS)
npm run gas-withdraw
npm run gas-send

# Проверка баланса первого кошелька
gaiad q bank balances $(gaiad keys show Wallet1 -a) --node https://cosmos-rpc.publicnode.com:443
```

## 🎛️ КОНФИГУРАЦИЯ

### Основные параметры (.env файл)
```env
# Количество кошельков для обработки
NUM_WALLETS=119

# Цена газа
GAS_PRICE=0.005

# Минимум наград для снятия (0.7 ATOM)
MIN_REWARDS_TO_WITHDRAW=700000

# Задержки между кошельками (1-2 часа)
MIN_DELAY=3600
MAX_DELAY=7200

# Уведомления
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Режимы
DEBUG_MODE=false
DRY_RUN=false
```

## 📊 ВОЗМОЖНОСТИ СИСТЕМЫ

### ✨ Ключевые функции
- 🤖 **Автоматическое снятие наград** с валидаторов
- 💸 **Отправка средств на биржи** (OKX, Bitget)
- ⚡ **Динамический расчет газа** на основе сети
- 🔄 **Отказоустойчивость** с множественными RPC
- 📈 **Детальная статистика** и мониторинг
- 🎨 **Красивый интерфейс** с цветным выводом

### 🧠 Умная логика
- **Adaptive Gas**: анализ последних блоков для точного расчета
- **RPC Load Balancing**: автопереключение между узлами
- **Error Recovery**: повторные попытки с увеличением газа
- **Transaction Monitoring**: отслеживание статуса операций
- **Random Delays**: защита от детекции ботов

## 🛡️ БЕЗОПАСНОСТЬ

### 🔒 Встроенная защита
- Случайные задержки между операциями (1-2 часа)
- Остатки на кошельках (15-25k uatom)
- Лимиты повторных попыток
- Мониторинг критических ошибок

### 📋 Рекомендации
1. **Всегда тестируйте** в DRY_RUN режиме сначала
2. **Используйте VPN** при работе с кошельками  
3. **Делайте бэкапы** keyring перед запуском
4. **Мониторьте логи** во время работы
5. **Начинайте с малых сумм** для тестирования

## 🆘 УСТРАНЕНИЕ НЕПОЛАДОК

### Частые проблемы:

**❌ "gaiad: command not found"**
```bash
wget https://github.com/cosmos/gaia/releases/latest/download/gaiad-linux-amd64
sudo mv gaiad-linux-amd64 /usr/local/bin/gaiad
sudo chmod +x /usr/local/bin/gaiad
```

**❌ "insufficient funds"**
```bash
# Проверьте баланс
gaiad q bank balances $(gaiad keys show Wallet1 -a) --node https://cosmos-rpc.publicnode.com:443
```

**❌ RPC errors**
```bash
# Проверьте состояние узлов
npm run health-check
```

## 🎉 ПОЗДРАВЛЯЕМ!

Ваша система **Cosmos Wallet Automation** полностью настроена и готова к работе!

### 🚀 Что дальше?
1. Создайте файлы с адресами кошельков
2. Добавьте кошельки в gaiad keyring  
3. Запустите `./start.sh` для интерактивной настройки
4. Начните с тестового режима
5. Мониторьте результаты в логах

### 📞 Поддержка
- 🐛 **Issues**: [GitHub Issues](https://github.com/zukaman/cosm/issues)
- 📧 **Email**: Создайте issue с описанием проблемы
- 📱 **Telegram**: @zukaman

---

**⚡ Удачной автоматизации!** Система создана для стабильной и безопасной работы с вашими Cosmos кошельками.