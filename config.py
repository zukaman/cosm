# config.py - Конфигурация для Cosmos автоматизации

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# ============================================================================
# ОСНОВНЫЕ ПАРАМЕТРЫ
# ============================================================================

GAS_PRICE = float(os.getenv('GAS_PRICE', 0.005))  # Цена газа в uatom
NUM_WALLETS = int(os.getenv('NUM_WALLETS', 119))  # Количество кошельков для обработки

# ============================================================================
# RPC УЗЛЫ
# ============================================================================

RPC_NODES = [
    "https://cosmos-rpc.publicnode.com:443",
    "https://cosmos-rpc.polkachu.com:443", 
    "https://cosmoshub-mainnet-rpc.itrocket.net"
]

# Добавляем кастомные RPC из переменных окружения
if os.getenv('CUSTOM_RPC_1'):
    RPC_NODES.append(os.getenv('CUSTOM_RPC_1'))
if os.getenv('CUSTOM_RPC_2'):
    RPC_NODES.append(os.getenv('CUSTOM_RPC_2'))
if os.getenv('CUSTOM_RPC_3'):
    RPC_NODES.append(os.getenv('CUSTOM_RPC_3'))

# ============================================================================
# ПОРОГИ ДЛЯ ОПЕРАЦИЙ
# ============================================================================

MIN_REWARDS_TO_WITHDRAW = int(os.getenv('MIN_REWARDS_TO_WITHDRAW', 700000))  # Минимум наград для снятия (uatom)
MIN_SEND_AMOUNT = int(os.getenv('MIN_SEND_AMOUNT', 50000))                  # Минимум для отправки (uatom)

# Остатки на кошельках
MIN_BALANCE_REMAIN = int(os.getenv('MIN_BALANCE_REMAIN', 15000))             # Минимальный остаток (uatom)
MAX_BALANCE_REMAIN = int(os.getenv('MAX_BALANCE_REMAIN', 25000))             # Максимальный остаток (uatom)

# ============================================================================
# ЗАДЕРЖКИ И ПОВТОРНЫЕ ПОПЫТКИ
# ============================================================================

# Задержки между операциями (секунды)
MIN_DELAY = int(os.getenv('MIN_DELAY', 3600))                # Минимальная задержка между кошельками (1 час)
MAX_DELAY = int(os.getenv('MAX_DELAY', 7200))                # Максимальная задержка (2 часа)

# Повторные попытки
MAX_WITHDRAW_ATTEMPTS = int(os.getenv('MAX_WITHDRAW_ATTEMPTS', 3))           # Попытки снятия наград
MAX_SEND_ATTEMPTS = int(os.getenv('MAX_SEND_ATTEMPTS', 3))                  # Попытки отправки
TX_CHECK_RETRIES = int(os.getenv('TX_CHECK_RETRIES', 10))                   # Проверки статуса транзакции
TX_CHECK_WAIT = int(os.getenv('TX_CHECK_WAIT', 30))                         # Ожидание между проверками (сек)

# ============================================================================
# ФАЙЛЫ КОШЕЛЬКОВ
# ============================================================================

OKX_WALLETS_FILE = os.getenv('OKX_WALLETS_FILE', 'okx_wallets')
BITGET_WALLETS_FILE = os.getenv('BITGET_WALLETS_FILE', 'bitget_wallets')
BINANCE_WALLETS_FILE = os.getenv('BINANCE_WALLETS_FILE', 'binance_wallets')

# Список поддерживаемых бирж
SUPPORTED_EXCHANGES = {
    'OKX': OKX_WALLETS_FILE,
    'Bitget': BITGET_WALLETS_FILE,
}

# Добавляем Binance если файл существует
if os.path.exists(BINANCE_WALLETS_FILE):
    SUPPORTED_EXCHANGES['Binance'] = BINANCE_WALLETS_FILE

# ============================================================================
# НАСТРОЙКИ ГАЗА
# ============================================================================

# Fallback значения газа
FALLBACK_GAS = {
    'withdraw': int(os.getenv('FALLBACK_WITHDRAW_GAS', 900000)),
    'send': int(os.getenv('FALLBACK_SEND_GAS', 250000))
}

# Множители для увеличения газа при ошибках
GAS_INCREASE_MULTIPLIER = {
    'withdraw': float(os.getenv('WITHDRAW_GAS_MULTIPLIER', 1.2)),  # +20%
    'send': float(os.getenv('SEND_GAS_MULTIPLIER', 1.1))          # +10%
}

# ============================================================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = os.getenv('LOG_DIR', 'logs')
LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'

# ============================================================================
# РЕЖИМЫ РАБОТЫ
# ============================================================================

DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'                   # Тестовый режим без реальных транзакций
SKIP_REWARDS_CHECK = os.getenv('SKIP_REWARDS_CHECK', 'false').lower() == 'true'

# ============================================================================
# УВЕДОМЛЕНИЯ
# ============================================================================

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# Discord Webhook
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
DISCORD_ENABLED = bool(DISCORD_WEBHOOK_URL)

# Email уведомления
EMAIL_SMTP_HOST = os.getenv('EMAIL_SMTP_HOST')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_TO = os.getenv('EMAIL_TO')
EMAIL_ENABLED = bool(EMAIL_SMTP_HOST and EMAIL_USERNAME and EMAIL_PASSWORD and EMAIL_TO)

# ============================================================================
# МОНИТОРИНГ
# ============================================================================

HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 300))         # 5 минут
STATS_UPDATE_INTERVAL = int(os.getenv('STATS_UPDATE_INTERVAL', 3600))        # 1 час
DAILY_REPORT_TIME = os.getenv('DAILY_REPORT_TIME', '09:00')                 # Время ежедневного отчета

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def get_config_summary():
    """Возвращает сводку текущей конфигурации"""
    return {
        'wallets_count': NUM_WALLETS,
        'gas_price': GAS_PRICE,
        'min_rewards': f"{MIN_REWARDS_TO_WITHDRAW:,} uatom ({MIN_REWARDS_TO_WITHDRAW/1_000_000:.6f} ATOM)",
        'rpc_nodes_count': len(RPC_NODES),
        'exchanges': list(SUPPORTED_EXCHANGES.keys()),
        'debug_mode': DEBUG_MODE,
        'dry_run': DRY_RUN,
        'notifications': {
            'telegram': TELEGRAM_ENABLED,
            'discord': DISCORD_ENABLED,
            'email': EMAIL_ENABLED
        }
    }

def validate_config():
    """Проверяет корректность конфигурации"""
    errors = []
    
    if NUM_WALLETS < 1 or NUM_WALLETS > 500:
        errors.append(f"NUM_WALLETS должно быть между 1 и 500, получено: {NUM_WALLETS}")
    
    if GAS_PRICE <= 0 or GAS_PRICE > 1:
        errors.append(f"GAS_PRICE должно быть между 0 и 1, получено: {GAS_PRICE}")
    
    if MIN_BALANCE_REMAIN >= MAX_BALANCE_REMAIN:
        errors.append(f"MIN_BALANCE_REMAIN ({MIN_BALANCE_REMAIN}) должно быть меньше MAX_BALANCE_REMAIN ({MAX_BALANCE_REMAIN})")
    
    if MIN_DELAY >= MAX_DELAY:
        errors.append(f"MIN_DELAY ({MIN_DELAY}) должно быть меньше MAX_DELAY ({MAX_DELAY})")
    
    if not RPC_NODES:
        errors.append("Должен быть указан хотя бы один RPC узел")
    
    return errors

# Автоматическая валидация при импорте
if __name__ != "__main__":
    config_errors = validate_config()
    if config_errors:
        print("⚠️ Ошибки в конфигурации:")
        for error in config_errors:
            print(f"  - {error}")
        print("Исправьте ошибки перед запуском системы.")
