import logging
import json
import os
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Style

init()

class CosmosLogger:
    def __init__(self, log_dir="logs", log_level="INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Настройка логгера
        self.logger = logging.getLogger("cosmos_automation")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Очищаем существующие хендлеры  
        self.logger.handlers.clear()
        
        # Файловый хендлер
        log_file = self.log_dir / f"cosmos_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Консольный хендлер
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_wallet_start(self, wallet_name, balance):
        message = f"[{wallet_name}] Начало обработки. Баланс: {balance:,} uatom"
        self.logger.info(message)
        print(f"{Fore.CYAN}🏦 {message}{Style.RESET_ALL}")
    
    def log_reward_withdrawal(self, wallet_name, rewards, tx_hash, success=True):
        status = "SUCCESS" if success else "FAILED"
        message = f"[{wallet_name}] Снятие наград: {rewards:,.2f} uatom - {status} - TX: {tx_hash}"
        self.logger.info(message)
        
        color = Fore.GREEN if success else Fore.RED
        print(f"{color}🎁 {message}{Style.RESET_ALL}")
    
    def log_send_transaction(self, wallet_name, amount, target, exchange, tx_hash, success=True):
        status = "SUCCESS" if success else "FAILED"
        message = f"[{wallet_name}] Отправка {amount:,} uatom на {exchange} - {status} - TX: {tx_hash}"
        self.logger.info(message)
        
        color = Fore.GREEN if success else Fore.RED
        print(f"{color}💸 {message}{Style.RESET_ALL}")
    
    def log_error(self, wallet_name, error_msg):
        message = f"[{wallet_name}] ОШИБКА: {error_msg}"
        self.logger.error(message)
        print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
    
    def log_gas_calculation(self, operation, gas_value):
        message = f"Gas расчет для {operation}: {gas_value:,}"
        self.logger.info(message)
        print(f"{Fore.BLUE}⛽ {message}{Style.RESET_ALL}")
    
    def log_info(self, message):
        self.logger.info(message)
        print(f"{Fore.WHITE}ℹ️ {message}{Style.RESET_ALL}")
    
    def log_warning(self, message):
        self.logger.warning(message)
        print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")
    
    def log_success(self, message):
        self.logger.info(message)
        print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
    
    def export_daily_stats(self, stats_data):
        """Экспорт ежедневной статистики"""
        try:
            stats_file = self.log_dir / f"stats_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.log_success(f"Статистика сохранена: {stats_file}")
        except Exception as e:
            self.log_error("SYSTEM", f"Ошибка сохранения статистики: {e}")

# Глобальный экземпляр логгера
_logger_instance = None

def get_logger():
    global _logger_instance
    if _logger_instance is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_dir = os.getenv('LOG_DIR', 'logs')
        _logger_instance = CosmosLogger(log_dir, log_level)
    return _logger_instance