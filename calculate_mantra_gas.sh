#!/bin/bash

# Количество блоков для анализа
BLOCKS_COUNT=100
NODE_URL="https://mantra-mainnet-rpc.itrocket.net"
ALT_NODE_URL="https://mantra-rpc.polkachu.com:443"  # Альтернативный RPC
TMP_FILE="/tmp/gas_data_send.json"

# Очистка временного файла
echo "[]" > $TMP_FILE

# Получаем последний блок
echo "Получаем последний блок с $NODE_URL..."
LAST_BLOCK_JSON=$(mantrachaind q block -o json --node $NODE_URL 2>/dev/null | grep -v "Falling back to latest block height:")
if [[ -z "$LAST_BLOCK_JSON" || "$LAST_BLOCK_JSON" == *"error"* ]]; then
    echo "Ошибка с $NODE_URL, пробуем $ALT_NODE_URL..."
    LAST_BLOCK_JSON=$(mantrachaind q block -o json --node $ALT_NODE_URL 2>/dev/null | grep -v "Falling back to latest block height:")
    NODE_URL=$ALT_NODE_URL
fi

LAST_BLOCK=$(echo "$LAST_BLOCK_JSON" | jq -r '.header.height' 2>/dev/null)

# Проверяем, является ли LAST_BLOCK числом
if ! [[ "$LAST_BLOCK" =~ ^[0-9]+$ ]]; then
    echo "Ошибка: Не удалось получить высоту последнего блока. Вывод: $LAST_BLOCK_JSON"
    exit 1
fi

FOUND_BLOCKS=0
CURRENT_HEIGHT=$LAST_BLOCK

echo "Собираем данные о газе из $BLOCKS_COUNT блоков с использованием $NODE_URL..."

while [[ "$FOUND_BLOCKS" -lt "$BLOCKS_COUNT" ]]; do
    echo "Проверяем блок $CURRENT_HEIGHT..."
    BLOCK_JSON=$(mantrachaind q block --type=height $CURRENT_HEIGHT -o json --node $NODE_URL 2>/dev/null)

    if [[ -z "$BLOCK_JSON" || "$BLOCK_JSON" == *"error"* ]]; then
        echo "Ошибка получения блока $CURRENT_HEIGHT."
        ((CURRENT_HEIGHT--))
        sleep 1  # Задержка 1 секунда
        continue
    fi

    # Фильтруем транзакции типа MsgSend
    FILTERED_TXS=$(echo "$BLOCK_JSON" | jq -c --arg height "$CURRENT_HEIGHT" '
        .block.data.txs | map(@base64d | fromjson) |
        map(select(.body.messages | any(.["@type"] == "/cosmos.bank.v1beta1.MsgSend"))) |
        map({height: ($height | tonumber), gas_used: (.auth_info.fee.gas_limit | tonumber)})
    ' 2>/dev/null)

    VALID_TX_COUNT=$(echo "$FILTERED_TXS" | jq 'length' 2>/dev/null)

    if [[ "$VALID_TX_COUNT" -gt 0 ]]; then
        echo "Найдено $VALID_TX_COUNT транзакций MsgSend в блоке $CURRENT_HEIGHT."
        echo "$FILTERED_TXS" >> $TMP_FILE
        ((FOUND_BLOCKS++))
    else
        echo "Транзакций MsgSend в блоке $CURRENT_HEIGHT не найдено."
    fi

    ((CURRENT_HEIGHT--))
    sleep 1  # Задержка между запросами
done

# Анализируем данные
echo "Анализируем собранные данные..."
AVERAGE_GAS=$(python3 <<EOF
import json

TMP_FILE = "$TMP_FILE"

try:
    with open(TMP_FILE, "r") as f:
        raw_data = f.readlines()
except Exception as e:
    print("⚠️ Ошибка чтения файла:", str(e))
    exit(1)

data = []
for block in raw_data:
    try:
        txs = json.loads(block)
        data.extend(txs)
    except json.JSONDecodeError as e:
        print(f"⚠️ Ошибка JSON-декодирования: {e}")
        continue

if not data:
    print(250000)  # Безопасное значение по умолчанию
    exit(0)

# Подсчёт среднего расхода газа
total_gas = sum(tx["gas_used"] for tx in data)
average_gas = total_gas / len(data)

# Добавляем 10% запаса и округляем до целого числа
adjusted_gas = int(round(average_gas * 1.1))

print(adjusted_gas)
EOF
)

rm -f $TMP_FILE

if [ -z "$AVERAGE_GAS" ]; then
    echo "Ошибка: Не удалось вычислить средний газ. Используем значение по умолчанию: 250000."
    AVERAGE_GAS=250000
else
    echo "Средний газ с запасом 10%: $AVERAGE_GAS"
fi

export MANTRA_AVERAGE_GAS=$AVERAGE_GAS
