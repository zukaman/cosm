#!/bin/bash

# Cosmos Wallet Automation - Стартовый скрипт
# Автоматическая проверка системы и запуск

set -e

echo " "
echo "🚀 ================================"
echo "🚀  Cosmos Wallet Automation    "
echo "🚀 ================================"
echo " "

# Проверка зависимостей
echo "🔍 Проверка системных требований..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не найден. Установите Node.js 16+"
    exit 1
fi

# Проверка gaiad
if ! command -v gaiad &> /dev/null; then
    echo "❌ gaiad не найден. Установите Cosmos SDK CLI"
    echo "   wget https://github.com/cosmos/gaia/releases/latest/download/gaiad-linux-amd64"
    echo "   sudo mv gaiad-linux-amd64 /usr/local/bin/gaiad"
    echo "   sudo chmod +x /usr/local/bin/gaiad"
    exit 1
fi

# Проверка jq
if ! command -v jq &> /dev/null; then
    echo "❌ jq не найден. Установите jq"
    echo "   sudo apt-get install jq"
    exit 1
fi

echo "✅ Все системные зависимости найдены"

# Проверка Python зависимостей
echo "🐍 Проверка Python зависимостей..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo "✅ Python зависимости установлены"
else
    echo "❌ Файл requirements.txt не найден"
    exit 1
fi

# Проверка Node.js зависимостей
echo "🟡 Проверка Node.js зависимостей..."
if [ -f "package.json" ]; then
    if [ ! -d "node_modules" ]; then
        echo "📦 Установка Node.js зависимостей..."
        npm install
    fi
    echo "✅ Node.js зависимости готовы"
else
    echo "❌ Файл package.json не найден"
    exit 1
fi

# Проверка файлов кошельков
echo "💼 Проверка файлов кошельков..."
if [ ! -f "okx_wallets" ] && [ ! -f "bitget_wallets" ]; then
    echo "❌ Не найдены файлы кошельков!"
    echo "   Создайте файлы okx_wallets и/или bitget_wallets"
    echo "   Используйте примеры: okx_wallets.example, bitget_wallets.example"
    exit 1
fi

# Подсчет адресов в файлах
if [ -f "okx_wallets" ]; then
    OKX_COUNT=$(grep -c "^cosmos1" okx_wallets || echo "0")
    echo "📊 OKX кошельков: $OKX_COUNT"
else
    OKX_COUNT=0
fi

if [ -f "bitget_wallets" ]; then
    BITGET_COUNT=$(grep -c "^cosmos1" bitget_wallets || echo "0")
    echo "📊 Bitget кошельков: $BITGET_COUNT"
else
    BITGET_COUNT=0
fi

TOTAL_WALLETS=$((OKX_COUNT + BITGET_COUNT))
if [ $TOTAL_WALLETS -lt 119 ]; then
    echo "⚠️  Всего адресов: $TOTAL_WALLETS (требуется минимум 119 для каждой биржи)"
    echo "   Добавьте больше адресов в файлы кошельков"
fi

# Проверка keyring
echo "🔐 Проверка кошельков в keyring..."
KEYRING_COUNT=$(gaiad keys list 2>/dev/null | grep -c "name:" || echo "0")
echo "📊 Кошельков в keyring: $KEYRING_COUNT"

if [ $KEYRING_COUNT -lt 119 ]; then
    echo "⚠️  В keyring недостаточно кошельков (требуется 119)"
    echo "   Добавьте кошельки командой: gaiad keys add WalletX --recover"
fi

# Создание папки для логов
mkdir -p logs

# Проверка RPC узлов
echo "🏥 Проверка состояния RPC узлов..."
npm run health-check

echo " "
echo "🎯 ================================"
echo "🎯  СИСТЕМА ГОТОВА К ЗАПУСКУ     "
echo "🎯 ================================"
echo " "

# Предложение вариантов запуска
echo "Выберите режим запуска:"
echo "1) 🧪 Тестовый режим (DRY_RUN=true)"
echo "2) 🚀 Рабочий режим"
echo "3) 📊 Только мониторинг"
echo "4) ⚙️  Тест расчета газа"
echo " "
read -p "Введите номер (1-4): " choice

case $choice in
    1)
        echo "🧪 Запуск в тестовом режиме..."
        export DRY_RUN=true
        python3 script.py
        ;;
    2)
        echo "🚀 Запуск в рабочем режиме..."
        echo "⚠️  ВНИМАНИЕ: Будут выполняться реальные транзакции!"
        read -p "Продолжить? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            export DRY_RUN=false
            python3 script.py
        else
            echo "Отменено пользователем"
        fi
        ;;
    3)
        echo "📊 Запуск мониторинга..."
        npm run monitor
        ;;
    4)
        echo "⚙️  Тестирование расчета газа..."
        echo "Тест расчета газа для снятия наград:"
        ./calculate_gas.sh
        echo " "
        echo "Тест расчета газа для отправки:"
        ./calculate_send_gas.sh
        echo " "
        echo "Современный JS расчет:"
        npm run gas-withdraw
        npm run gas-send
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo " "
echo "✅ Выполнение завершено!"
echo "📋 Логи сохранены в папке logs/"