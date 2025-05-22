import subprocess
import time
import json
import random
from colorama import init, Fore, Style

init()

GAS_PRICE = 0.005
NUM_WALLETS = 119

# RPC узлы для всех операций
RPC_NODES = [
    "https://cosmos-rpc.publicnode.com:443",
    "https://cosmos-rpc.polkachu.com:443",
    "https://cosmoshub-mainnet-rpc.itrocket.net"
]

def get_random_rpc():
    """Получить случайный RPC узел"""
    return random.choice(RPC_NODES)

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{Fore.RED}Ошибка выполнения команды '{command}': {result.stderr}{Fore.RESET}")
    return result.stdout.strip()

def get_withdraw_gas_estimate(retries=5):
    for attempt in range(retries):
        try:
            result = subprocess.run(["bash", "calculate_gas.sh"], capture_output=True, text=True, check=True)
            gas_used = result.stdout.strip()
            if gas_used and gas_used.replace('.', '').isdigit():
                gas_value = int(round(float(gas_used)))
                print(f"{Fore.YELLOW}Получен актуальный gas_used для снятия наград: {gas_value}{Fore.RESET}")
                return gas_value
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}❌ Ошибка выполнения calculate_gas.sh. Попытка {attempt + 1}/{retries}{Fore.RESET}")
    print(f"{Fore.YELLOW}⚠️ Не удалось получить gas_used для снятия наград. Используем запасное значение (900000).{Fore.RESET}")
    return 900000

def get_send_gas_estimate(retries=5):
    for attempt in range(retries):
        try:
            result = subprocess.run(["bash", "calculate_send_gas.sh"], capture_output=True, text=True, check=True)
            gas_used = result.stdout.strip()
            if gas_used and gas_used.replace('.', '').isdigit():
                gas_value = int(round(float(gas_used)))
                print(f"{Fore.YELLOW}Получен актуальный gas_used для отправки: {gas_value}{Fore.RESET}")
                return gas_value
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}❌ Ошибка выполнения calculate_send_gas.sh. Попытка {attempt + 1}/{retries}{Fore.RESET}")
    print(f"{Fore.YELLOW}⚠️ Не удалось получить gas_used для отправки. Используем запасное значение (250000).{Fore.RESET}")
    return 250000

def calculate_fees(gas_used):
    return int(gas_used * GAS_PRICE) + 1

def check_transaction(tx_hash, max_retries=10, wait_time=30):
    if not tx_hash:
        return False
    for attempt in range(max_retries):
        for rpc in RPC_NODES:
            tx_info = run_command(f"gaiad q tx {tx_hash} --node {rpc} -o json")
            if not tx_info:
                continue
            try:
                tx_data = json.loads(tx_info)
                if tx_data.get("code", 1) == 0:
                    return True
                elif tx_data.get("code") == 11 and "out of gas" in tx_data.get("raw_log", "").lower():
                    print(f"{Fore.RED}[Ошибка] Код ошибки {tx_data.get('code')}: {tx_data.get('raw_log')}{Fore.RESET}")
                    return "out_of_gas"
                else:
                    print(f"{Fore.RED}[Ошибка] Код ошибки {tx_data.get('code')}: {tx_data.get('raw_log')}{Fore.RESET}")
                    return False
            except json.JSONDecodeError:
                print(f"{Fore.CYAN}[Ожидание] Транзакция {tx_hash} не найдена на {rpc}. Попытка {attempt + 1}/{max_retries}...{Fore.RESET}")
                continue
        time.sleep(wait_time)
    print(f"{Fore.YELLOW}⚠️ Транзакция {tx_hash} не подтверждена после {max_retries} попыток{Fore.RESET}")
    return False

def get_current_balance(addr):
    rpc = get_random_rpc()
    balance_json = run_command(f"gaiad q bank balances {addr} --node {rpc} -o json")
    try:
        balance_data = json.loads(balance_json)
        return next((int(b["amount"]) for b in balance_data.get("balances", []) if b["denom"] == "uatom"), 0)
    except (json.JSONDecodeError, KeyError, ValueError):
        return 0

def main():
    try:
        with open("okx_wallets") as f:
            okx_wallets = f.read().splitlines()
    except FileNotFoundError:
        okx_wallets = []
    
    try:
        with open("bitget_wallets") as f:
            bitget_wallets = f.read().splitlines()
    except FileNotFoundError:
        bitget_wallets = []

    if not okx_wallets and not bitget_wallets:
        print(f"{Fore.RED}❌ Ошибка: нет доступных файлов кошельков!{Fore.RESET}")
        return
    
    if len(okx_wallets) < NUM_WALLETS and len(bitget_wallets) < NUM_WALLETS:
        print(f"{Fore.RED}❌ Ошибка: недостаточно адресов в файлах (okx: {len(okx_wallets)}, bitget: {len(bitget_wallets)}), требуется {NUM_WALLETS}{Fore.RESET}")
        return

    available_wallets = []
    if okx_wallets and len(okx_wallets) >= NUM_WALLETS:
        available_wallets.append(("OKX", okx_wallets))
    if bitget_wallets and len(bitget_wallets) >= NUM_WALLETS:
        available_wallets.append(("Bitget", bitget_wallets))

    if not available_wallets:
        print(f"{Fore.RED}❌ Ошибка: нет файлов с достаточным количеством адресов!{Fore.RESET}")
        return

    wallet_targets = {}
    for i in range(NUM_WALLETS):
        wallet_name = f"Wallet{i+1}"
        if len(available_wallets) == 2:
            exchange, wallet_list = random.choice(available_wallets)
        else:
            exchange, wallet_list = available_wallets[0]
        wallet_targets[wallet_name] = (exchange, wallet_list[i])

    wallet_indices = list(range(NUM_WALLETS))
    random.shuffle(wallet_indices)

    for i in wallet_indices:
        wallet_name = f"Wallet{i+1}"
        addr = run_command(f"gaiad keys show {wallet_name} -a")
        exchange, target_wallet = wallet_targets[wallet_name]

        # Красивый заголовок начала обработки кошелька
        print(f"\n{Fore.CYAN}{'='*60}{Fore.RESET}")
        print(f"{Fore.WHITE}{Style.BRIGHT}🏦 [ {wallet_name} ] {Style.RESET_ALL}{Fore.CYAN}Начинаем обработку... ({i+1}/{len(wallet_indices)}){Fore.RESET}")
        print(f"{Fore.CYAN}{'='*60}{Fore.RESET}")

        initial_balance = get_current_balance(addr)
        print(f"{Fore.WHITE}💰 [ {wallet_name} ]{Fore.YELLOW} Начальный баланс: {Fore.GREEN}{Style.BRIGHT}{initial_balance:,}{Style.RESET_ALL}{Fore.YELLOW} uatom{Fore.RESET}")

        withdraw_gas = get_withdraw_gas_estimate()
        withdraw_fees = calculate_fees(withdraw_gas)
        print(f"{Fore.WHITE}⛽ [ {wallet_name} ]{Fore.BLUE} Gas для снятия: {Fore.CYAN}{withdraw_gas:,}{Fore.BLUE}, комиссия: {Fore.CYAN}{withdraw_fees:,}{Fore.BLUE} uatom{Fore.RESET}")

        if initial_balance < withdraw_fees:
            print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Недостаточно средств для комиссии ({initial_balance:,} < {withdraw_fees:,} uatom){Style.RESET_ALL}{Fore.RESET}")
            continue

        rewards = run_command(f"gaiad q distribution rewards {wallet_name} --node {get_random_rpc()} -o json | jq -r '.total[] | select(test(\"uatom$\")) | split(\"uatom\")[0]'")
        rewards = float(rewards) if rewards else 0.0
        
        if rewards > 0:
            print(f"{Fore.WHITE}🎁 [ {wallet_name} ]{Fore.MAGENTA} Доступно наград: {Fore.YELLOW}{Style.BRIGHT}{rewards:,.2f}{Style.RESET_ALL}{Fore.MAGENTA} uatom{Fore.RESET}")
        else:
            print(f"{Fore.WHITE}🎁 [ {wallet_name} ]{Fore.RED} Награды отсутствуют{Fore.RESET}")

        reward_tx_confirmed = False
        action_performed = False  # Флаг для отслеживания выполненных действий
        min_rewards_to_withdraw = 700000
        if rewards >= min_rewards_to_withdraw:
            print(f"{Fore.WHITE}✅ [ {wallet_name} ]{Fore.GREEN} Начинаем снятие наград ({rewards:,.2f} uatom)...{Fore.RESET}")
            max_attempts = 3
            attempt = 0
            current_balance = initial_balance
            while attempt < max_attempts:
                if current_balance < withdraw_fees:
                    print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Недостаточно средств после попытки {attempt} ({current_balance:,} < {withdraw_fees:,} uatom){Style.RESET_ALL}{Fore.RESET}")
                    break

                rpc = get_random_rpc()
                reward_tx = run_command(
                    f"gaiad tx distribution withdraw-all-rewards --from {wallet_name} "
                    f"--fees {withdraw_fees}uatom --gas {withdraw_gas} --node {rpc} -y -o json"
                )
                try:
                    reward_tx_json = json.loads(reward_tx)
                    reward_tx_hash = reward_tx_json.get("txhash", "")
                    print(f"{Fore.WHITE}📤 [ {wallet_name} ]{Fore.CYAN} Хеш снятия: {Fore.BLUE}{Style.BRIGHT}{reward_tx_hash}{Style.RESET_ALL}{Fore.RESET}")
                except json.JSONDecodeError:
                    print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Ошибка разбора JSON транзакции снятия{Style.RESET_ALL}{Fore.RESET}")
                    break

                print(f"{Fore.WHITE}🔍 [ {wallet_name} ]{Fore.CYAN} Проверяем транзакцию через 30 секунд...{Fore.RESET}")
                time.sleep(30)
                tx_status = check_transaction(reward_tx_hash)
                if tx_status == "out_of_gas":
                    attempt += 1
                    withdraw_gas = int(withdraw_gas * 1.2)
                    withdraw_fees = calculate_fees(withdraw_gas)
                    current_balance = get_current_balance(addr)
                    print(f"{Fore.WHITE}💳 [ {wallet_name} ]{Fore.YELLOW} Баланс после попытки {attempt}: {Fore.CYAN}{current_balance:,}{Fore.YELLOW} uatom{Fore.RESET}")
                    print(f"{Fore.WHITE}⚠️  [ {wallet_name} ]{Fore.YELLOW} Увеличиваем gas до {Fore.CYAN}{withdraw_gas:,}{Fore.YELLOW}, повторяем (попытка {attempt}/{max_attempts}){Fore.RESET}")
                    continue
                elif tx_status is True:
                    print(f"{Fore.WHITE}✅ [ {wallet_name} ]{Fore.GREEN}{Style.BRIGHT} Награды успешно сняты!{Style.RESET_ALL}{Fore.RESET}")
                    reward_tx_confirmed = True
                    action_performed = True  # Действие выполнено
                    break
                else:
                    print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Транзакция не подтверждена{Style.RESET_ALL}{Fore.RESET}")
                    break
            if not reward_tx_confirmed:
                print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Не удалось снять награды после {max_attempts} попыток{Style.RESET_ALL}{Fore.RESET}")
        else:
            print(f"{Fore.WHITE}⏭️  [ {wallet_name} ]{Fore.YELLOW} Награды ({rewards:,.2f}) < порога ({min_rewards_to_withdraw:,}), пропускаем{Fore.RESET}")

        current_balance = get_current_balance(addr)
        print(f"{Fore.WHITE}💳 [ {wallet_name} ]{Fore.YELLOW} Баланс после снятия: {Fore.GREEN}{Style.BRIGHT}{current_balance:,}{Style.RESET_ALL}{Fore.YELLOW} uatom{Fore.RESET}")

        min_balance = min(15000, current_balance)
        max_balance = min(25000, current_balance)
        if min_balance > max_balance:
            min_balance, max_balance = max_balance, min_balance
        if min_balance == max_balance:
            remaining_balance = min_balance
        else:
            remaining_balance = random.randint(min_balance, max_balance)
        send_amount = current_balance - remaining_balance if current_balance > remaining_balance else 0
        
        print(f"{Fore.WHITE}📊 [ {wallet_name} ]{Fore.BLUE} Расчет отправки:{Fore.RESET}")
        print(f"   {Fore.YELLOW}├─ Баланс: {Fore.CYAN}{Style.BRIGHT}{current_balance:,}{Style.RESET_ALL}{Fore.YELLOW} uatom{Fore.RESET}")
        print(f"   {Fore.YELLOW}├─ Оставляем: {Fore.GREEN}{remaining_balance:,}{Fore.YELLOW} uatom{Fore.RESET}")
        print(f"   {Fore.YELLOW}└─ Отправляем: {Fore.MAGENTA}{Style.BRIGHT}{send_amount:,}{Style.RESET_ALL}{Fore.YELLOW} uatom{Fore.RESET}")

        send_gas = get_send_gas_estimate()
        send_fees = calculate_fees(send_gas)
        min_send_amount = max(send_fees + 3000, 50000)  # Минимум 50000 uatom для отправки
        print(f"{Fore.WHITE}⛽ [ {wallet_name} ]{Fore.BLUE} Gas для отправки: {Fore.CYAN}{send_gas:,}{Fore.BLUE}, минимум: {Fore.CYAN}{min_send_amount:,}{Fore.BLUE} uatom{Fore.RESET}")
        
        if send_amount >= min_send_amount:
            if current_balance < send_fees:
                print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Недостаточно средств для комиссии ({current_balance:,} < {send_fees:,} uatom){Style.RESET_ALL}{Fore.RESET}")
            else:
                max_send_attempts = 3  # Ограничим количество попыток отправки
                attempt = 0
                current_send_gas = send_gas
                current_send_fees = send_fees
                while attempt < max_send_attempts:
                    print(f"{Fore.WHITE}🚀 [ {wallet_name} ]{Fore.GREEN} Отправляем {Fore.MAGENTA}{Style.BRIGHT}{send_amount:,}{Style.RESET_ALL}{Fore.GREEN} uatom на {Fore.BLUE}{exchange}{Fore.GREEN} (попытка {attempt + 1}/{max_send_attempts}){Fore.RESET}")
                    print(f"   {Fore.CYAN}└─ Адрес: {Fore.WHITE}{target_wallet}{Fore.RESET}")
                    rpc = get_random_rpc()
                    send_tx = run_command(
                        f"gaiad tx bank send {addr} {target_wallet} {send_amount}uatom "
                        f"--from {wallet_name} --fees {current_send_fees}uatom --gas {current_send_gas} --node {rpc} -y -o json"
                    )
                    try:
                        send_tx_json = json.loads(send_tx)
                        send_tx_hash = send_tx_json.get("txhash", "")
                        print(f"{Fore.WHITE}📤 [ {wallet_name} ]{Fore.CYAN} Хеш отправки: {Fore.BLUE}{Style.BRIGHT}{send_tx_hash}{Style.RESET_ALL}{Fore.RESET}")
                    except json.JSONDecodeError:
                        print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Ошибка разбора JSON транзакции отправки{Style.RESET_ALL}{Fore.RESET}")
                        break

                    print(f"{Fore.WHITE}🔍 [ {wallet_name} ]{Fore.CYAN} Проверяем транзакцию через 30 секунд...{Fore.RESET}")
                    time.sleep(30)
                    tx_status = check_transaction(send_tx_hash)
                    if tx_status == "out_of_gas":
                        attempt += 1
                        current_send_gas = int(current_send_gas * 1.1)
                        current_send_fees = calculate_fees(current_send_gas)
                        current_balance = get_current_balance(addr)
                        print(f"{Fore.WHITE}💳 [ {wallet_name} ]{Fore.YELLOW} Баланс после попытки {attempt}: {Fore.CYAN}{current_balance:,}{Fore.YELLOW} uatom{Fore.RESET}")
                        print(f"{Fore.WHITE}⚠️  [ {wallet_name} ]{Fore.YELLOW} Увеличиваем газ до {Fore.CYAN}{current_send_gas:,}{Fore.YELLOW}, повторяем (попытка {attempt}/{max_send_attempts}){Fore.RESET}")
                        continue
                    elif tx_status is True:
                        print(f"{Fore.WHITE}✅ [ {wallet_name} ]{Fore.GREEN}{Style.BRIGHT} Отправлено {Fore.MAGENTA}{send_amount:,}{Fore.GREEN} uatom на {Fore.BLUE}{exchange}{Style.RESET_ALL}{Fore.RESET}")
                        print(f"   {Fore.CYAN}└─ Адрес: {Fore.WHITE}{target_wallet}{Fore.RESET}")
                        action_performed = True  # Действие выполнено
                        break
                    else:
                        print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Ошибка отправки {send_amount:,} uatom на {exchange}{Style.RESET_ALL}{Fore.RESET}")
                        print(f"   {Fore.CYAN}└─ Адрес: {Fore.WHITE}{target_wallet}{Fore.RESET}")
                        break
                if attempt >= max_send_attempts:
                    print(f"{Fore.WHITE}❌ [ {wallet_name} ]{Fore.RED}{Style.BRIGHT} Не удалось отправить средства после {max_send_attempts} попыток{Style.RESET_ALL}{Fore.RESET}")
        else:
            print(f"{Fore.WHITE}⏭️  [ {wallet_name} ]{Fore.YELLOW} Сумма {Fore.RED}{send_amount:,}{Fore.YELLOW} < минимума {Fore.RED}{min_send_amount:,}{Fore.YELLOW}, пропускаем{Fore.RESET}")

        # Завершение обработки кошелька
        print(f"{Fore.GREEN}{'='*60}")
        if action_performed:
            print(f"{Fore.GREEN}{Style.BRIGHT}✅ [ {wallet_name} ] ЗАВЕРШЕНО С ДЕЙСТВИЯМИ{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}{Style.BRIGHT}⚡ [ {wallet_name} ] ЗАВЕРШЕНО БЕЗ ДЕЙСТВИЙ{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Fore.RESET}")

        # Задержка только если было выполнено какое-то действие (снятие наград или отправка)
        if action_performed:
            delay = random.randint(3600, 7200)
            print(f"\n{Fore.CYAN}⏳ [ {wallet_name} ]{Fore.YELLOW} Ожидание {Fore.CYAN}{Style.BRIGHT}{delay:,}{Style.RESET_ALL}{Fore.YELLOW} секунд до следующего кошелька...{Fore.RESET}")
            print(f"{Fore.CYAN}{'─'*60}{Fore.RESET}\n")
            time.sleep(delay)
        else:
            print(f"{Fore.WHITE}⚡ [ {wallet_name} ]{Fore.BLUE} Переходим к следующему кошельку без задержки{Fore.RESET}")
            print(f"{Fore.CYAN}{'─'*60}{Fore.RESET}\n")

if __name__ == "__main__":
    main()
