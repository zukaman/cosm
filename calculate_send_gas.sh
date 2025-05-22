#!/bin/bash

# Количество блоков с транзакциями отправки, которые нужно собрать
BLOCKS_COUNT=5
NODE_URL="https://cosmos-rpc.publicnode.com:443"
TMP_FILE="/tmp/gas_data_send.json"

# Очистка временного файла
echo "[]" > $TMP_FILE

# Получаем последний блок
LAST_BLOCK_JSON=$(gaiad q block -o json --node $NODE_URL 2>/dev/null | tail -n +2)
LAST_BLOCK=$(echo "$LAST_BLOCK_JSON" | jq -r '.header.height' 2>/dev/null)

# Проверяем, является ли LAST_BLOCK числом
if ! [[ "$LAST_BLOCK" =~ ^[0-9]+$ ]]; then
    exit 1
fi

FOUND_BLOCKS=0
CURRENT_HEIGHT=$LAST_BLOCK

while [[ "$FOUND_BLOCKS" -lt "$BLOCKS_COUNT" ]]; do
    TXS_JSON=$(gaiad q txs --query "tx.height=$CURRENT_HEIGHT" -o json --node $NODE_URL 2>/dev/null)

    if [[ -z "$TXS_JSON" || "$TXS_JSON" == *"error"* ]]; then
        ((CURRENT_HEIGHT--))
        continue
    fi

    FILTERED_TXS=$(echo "$TXS_JSON" | jq -c '[.txs[] | select(.tx.body.messages[]."@type" == "/cosmos.bank.v1beta1.MsgSend") | 
        {height: (.height | tonumber), 
         gas_used: (.gas_used | tonumber)}]')

    VALID_TX_COUNT=$(echo "$FILTERED_TXS" | jq 'length')

    if [[ "$VALID_TX_COUNT" -gt 0 ]]; then
        echo "$FILTERED_TXS" >> $TMP_FILE
        ((FOUND_BLOCKS++))
    fi

    ((CURRENT_HEIGHT--))
done

# Анализируем данные
python3 <<EOF
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

# Добавляем 5% запаса и округляем до целого числа
adjusted_gas = int(round(average_gas * 1.1))

print(adjusted_gas)
EOF

rm -f $TMP_FILE
