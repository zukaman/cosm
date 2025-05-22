# Быстрая настройка Cosmos Wallet Automation

Эта инструкция поможет вам быстро запустить систему автоматизации.

## 🚀 Шаг 1: Установка зависимостей

```bash
# Клонируем репозиторий
git clone https://github.com/zukaman/cosm.git
cd cosm

# Устанавливаем Python зависимости
pip install -r requirements.txt

# Устанавливаем Node.js зависимости
npm install

# Делаем bash скрипты исполняемыми
chmod +x *.sh
```

## 💼 Шаг 2: Подготовка кошельков

### Добавление кошельков в gaiad
```bash
# Добавляем каждый кошелек в keyring
gaiad keys add Wallet1 --recover
gaiad keys add Wallet2 --recover
# ... повторить для всех 119 кошельков

# Проверяем что все кошельки добавлены
gaiad keys list
```

### Создание файлов с адресами бирж

Создайте файл `okx_wallets`:
```
cosmos1abc123def456ghi789jkl012mno345pqr678stu901
cosmos1vwx234yza567bcd890efg123hij456klm789nop012
cosmos1qrs345tuv678wxy901zab234cde567fgh890ijk123
...
```

Создайте файл `bitget_wallets`:
```
cosmos1def456ghi789jkl012mno345pqr678stu901vwx234
cosmos1yza567bcd890efg123hij456klm789nop012qrs345
cosmos1tuv678wxy901zab234cde567fgh890ijk123lmn456
...
```

**Важно:** Каждый файл должен содержать минимум 119 валидных Cosmos адресов.

## ⚙️ Шаг 3: Базовая конфигурация

Скопируйте файл конфигурации:
```bash
cp .env.example .env
```

Отредактируйте `.env` файл под ваши потребности:
```env
# Основные настройки
NUM_WALLETS=119
GAS_PRICE=0.005
MIN_REWARDS_TO_WITHDRAW=700000

# Уведомления (опционально)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🧪 Шаг 4: Тестирование системы

### Проверка RPC узлов
```bash
npm run health-check
```

### Тест расчета газа
```bash
# Тест расчета газа для снятия наград
./calculate_gas.sh

# Тест расчета газа для отправки
./calculate_send_gas.sh

# Современный JS расчет
npm run gas-withdraw
npm run gas-send
```

### Проверка баланса кошельков
```bash
# Проверяем первые несколько кошельков
for i in {1..5}; do
  echo "Wallet$i:"
  gaiad q bank balances $(gaiad keys show Wallet$i -a) --node https://cosmos-rpc.publicnode.com:443
done
```

## 🎮 Шаг 5: Запуск системы

### Тестовый режим (без реальных транзакций)
```bash
# Установите в .env файле
echo "DRY_RUN=true" >> .env

# Запустите скрипт
python script.py
```

### Боевой режим
```bash
# Убедитесь что DRY_RUN=false
echo "DRY_RUN=false" >> .env

# Запуск основного скрипта
python script.py
```

## 📊 Мониторинг

### Просмотр логов в реальном времени
```bash
tail -f logs/cosmos_$(date +%Y%m%d).log
```

### Проверка статистики
```bash
# JavaScript мониторинг
npm run monitor

# Ручная проверка статистики
python -c "
from config import *
print('Конфигурация:')
print(f'Кошельков: {NUM_WALLETS}')
print(f'Цена газа: {GAS_PRICE}')
print(f'RPC узлов: {len(RPC_NODES)}')
"
```

## 🚨 Частые проблемы

### Ошибка "gaiad: command not found"
```bash
# Скачайте и установите gaiad
wget https://github.com/cosmos/gaia/releases/latest/download/gaiad-linux-amd64
sudo mv gaiad-linux-amd64 /usr/local/bin/gaiad
sudo chmod +x /usr/local/bin/gaiad
```

### Ошибка "insufficient funds"
```bash
# Проверьте баланс
gaiad q bank balances $(gaiad keys show Wallet1 -a) --node https://cosmos-rpc.publicnode.com:443

# Убедитесь что на кошельках есть средства для комиссий
```

### Проблемы с keyring
```bash
# Проверьте что все кошельки добавлены
gaiad keys list | wc -l  # Должно быть 119

# Если кошелек не найден
gaiad keys show Wallet1 -a || echo "Wallet1 не найден"
```

## 🔒 Безопасность

1. **Используйте VPN** при работе с кошельками
2. **Сделайте бэкап keyring** перед запуском
3. **Тестируйте на небольших суммах** сначала
4. **Мониторьте логи** во время работы

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи в папке `logs/`
2. Запустите `npm run health-check`
3. Создайте issue на GitHub с описанием проблемы и логами

---

**Готово!** Ваша система автоматизации Cosmos готова к работе. 🚀