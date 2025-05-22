// js/gas-calculator.js
// Современный расчет газа с использованием CosmJS

import { StargateClient } from "@cosmjs/stargate";
import { Tendermint34Client } from "@cosmjs/tendermint-rpc";
import chalk from "chalk";

export class GasCalculator {
  constructor(rpcEndpoints) {
    this.rpcEndpoints = rpcEndpoints;
    this.fallbackGas = {
      withdraw: 900000,
      send: 250000
    };
    this.cache = new Map();
    this.cacheTimeout = 300000; // 5 минут
  }

  async getRandomRPC() {
    return this.rpcEndpoints[Math.floor(Math.random() * this.rpcEndpoints.length)];
  }

  async withRetry(operation, maxRetries = 3) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        console.log(chalk.yellow(`⚠️ Попытка ${attempt + 1}/${maxRetries} неудачна: ${error.message}`));
        if (attempt === maxRetries - 1) throw error;
        await this.sleep(1000 * (attempt + 1)); // Экспоненциальная задержка
      }
    }
  }

  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  getCacheKey(messageType, blocksCount) {
    return `${messageType}_${blocksCount}`;
  }

  isValidCache(cacheEntry) {
    return cacheEntry && (Date.now() - cacheEntry.timestamp < this.cacheTimeout);
  }

  async analyzeBlocks(messageType, blocksCount = 5) {
    // Проверяем кэш
    const cacheKey = this.getCacheKey(messageType, blocksCount);
    const cached = this.cache.get(cacheKey);
    if (this.isValidCache(cached)) {
      console.log(chalk.cyan(`📋 Используем кэшированный результат для ${messageType}`));
      return cached.value;
    }

    const rpcUrl = await this.getRandomRPC();
    console.log(chalk.blue(`🔍 Анализируем блоки на ${rpcUrl}...`));
    
    try {
      const result = await this.withRetry(async () => {
        const tmClient = await Tendermint34Client.connect(rpcUrl);
        
        // Получаем последний блок
        const status = await tmClient.status();
        const latestHeight = status.syncInfo.latestBlockHeight;
        
        console.log(chalk.gray(`📊 Анализируем с блока ${latestHeight}...`));
        
        const gasData = [];
        let currentHeight = latestHeight;
        let foundBlocks = 0;
        let checkedBlocks = 0;
        const maxBlocksToCheck = blocksCount * 20; // Лимит проверки блоков

        while (foundBlocks < blocksCount && checkedBlocks < maxBlocksToCheck && currentHeight > 0) {
          try {
            // Получаем блок через REST API (более стабильно)
            const blockUrl = `${rpcUrl.replace(':443', '')}/block?height=${currentHeight}`;
            const blockResponse = await fetch(blockUrl);
            
            if (!blockResponse.ok) {
              currentHeight--;
              continue;
            }

            const blockData = await blockResponse.json();
            checkedBlocks++;
            
            if (!blockData.result?.block?.data?.txs || blockData.result.block.data.txs.length === 0) {
              currentHeight--;
              continue;
            }

            // Анализируем транзакции через REST API
            const relevantTxs = await this.analyzeBlockTransactionsREST(currentHeight, messageType, rpcUrl);

            if (relevantTxs.length > 0) {
              gasData.push(...relevantTxs);
              foundBlocks++;
              console.log(chalk.green(`✅ Блок ${currentHeight}: найдено ${relevantTxs.length} транзакций ${messageType}`));
            }
          } catch (blockError) {
            console.log(chalk.yellow(`⚠️ Ошибка блока ${currentHeight}: ${blockError.message}`));
          }
          
          currentHeight--;
        }

        if (gasData.length === 0) {
          throw new Error(`Не найдено транзакций типа ${messageType} в последних ${checkedBlocks} блоках`);
        }

        const calculatedGas = this.calculateAverageGas(gasData, messageType);
        
        // Кэшируем результат
        this.cache.set(cacheKey, {
          value: calculatedGas,
          timestamp: Date.now()
        });

        return calculatedGas;
      });

      return result;
      
    } catch (error) {
      console.error(chalk.red(`❌ Ошибка анализа блоков: ${error.message}`));
      return this.fallbackGas[messageType === 'withdraw' ? 'withdraw' : 'send'];
    }
  }

  async analyzeBlockTransactionsREST(height, messageType, rpcUrl) {
    try {
      // Получаем транзакции блока через REST API
      const txsUrl = `${rpcUrl.replace(':443', '')}/tx_search?query="tx.height=${height}"&per_page=100`;
      const response = await fetch(txsUrl);
      
      if (!response.ok) return [];
      
      const data = await response.json();
      const txs = data.result?.txs || [];
      
      const relevantTxs = [];
      
      for (const tx of txs) {
        try {
          // Декодируем транзакцию (упрощенная версия)
          const txResult = tx.tx_result;
          if (txResult.code !== 0) continue; // Пропускаем неуспешные транзакции
          
          // Проверяем события транзакции на наличие нужного типа сообщения
          const hasRelevantMessage = this.checkTransactionEvents(txResult.events, messageType);
          
          if (hasRelevantMessage) {
            const gasUsed = parseInt(txResult.gas_used);
            const gasWanted = parseInt(txResult.gas_wanted);
            
            if (gasUsed > 0 && gasUsed < gasWanted * 1.5) { // Фильтруем аномальные значения
              relevantTxs.push({
                gasUsed,
                gasWanted,
                height: parseInt(height)
              });
            }
          }
        } catch (txError) {
          // Пропускаем транзакции, которые не удалось обработать
          continue;
        }
      }
      
      return relevantTxs;
    } catch (error) {
      console.log(chalk.yellow(`⚠️ Ошибка анализа транзакций блока ${height}: ${error.message}`));
      return [];
    }
  }

  checkTransactionEvents(events, messageType) {
    if (!events || !Array.isArray(events)) return false;
    
    const targetEventType = messageType === 'withdraw' 
      ? 'withdraw_rewards' 
      : 'transfer';
    
    return events.some(event => 
      event.type === targetEventType || 
      event.type === 'message' && 
      event.attributes?.some(attr => 
        attr.key === 'action' && 
        (messageType === 'withdraw' ? 
          attr.value?.includes('withdraw') : 
          attr.value?.includes('send'))
      )
    );
  }

  calculateAverageGas(gasData, messageType) {
    if (gasData.length === 0) {
      return this.fallbackGas[messageType === 'withdraw' ? 'withdraw' : 'send'];
    }

    // Фильтруем выбросы (убираем слишком большие и маленькие значения)
    const sortedGas = gasData.map(tx => tx.gasUsed).sort((a, b) => a - b);
    const q1Index = Math.floor(sortedGas.length * 0.25);
    const q3Index = Math.floor(sortedGas.length * 0.75);
    const q1 = sortedGas[q1Index];
    const q3 = sortedGas[q3Index];
    const iqr = q3 - q1;
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;
    
    const filteredData = gasData.filter(tx => 
      tx.gasUsed >= lowerBound && tx.gasUsed <= upperBound
    );

    if (filteredData.length === 0) {
      return this.fallbackGas[messageType === 'withdraw' ? 'withdraw' : 'send'];
    }

    // Вычисляем среднее значение
    const totalGas = filteredData.reduce((sum, tx) => sum + tx.gasUsed, 0);
    const averageGas = totalGas / filteredData.length;

    // Добавляем запас (5% для снятия, 10% для отправки)
    const margin = messageType === 'withdraw' ? 1.05 : 1.1;
    const adjustedGas = Math.round(averageGas * margin);

    console.log(chalk.blue(`📊 Gas анализ (${messageType}):`), {
      samplesTotal: gasData.length,
      samplesFiltered: filteredData.length,
      averageGas: Math.round(averageGas).toLocaleString(),
      adjustedGas: adjustedGas.toLocaleString(),
      margin: `+${((margin - 1) * 100).toFixed(1)}%`
    });

    return adjustedGas;
  }

  // Публичные методы для основного скрипта
  async getWithdrawGas(retries = 3) {
    console.log(chalk.cyan('🔍 Расчет газа для снятия наград...'));
    
    try {
      const gas = await this.analyzeBlocks('withdraw', 5);
      console.log(chalk.green(`✅ Получен gas для снятия: ${gas.toLocaleString()}`));
      return gas;
    } catch (error) {
      console.log(chalk.red(`❌ Ошибка расчета газа: ${error.message}`));
      console.log(chalk.yellow(`⚠️ Используем fallback значение: ${this.fallbackGas.withdraw.toLocaleString()}`));
      return this.fallbackGas.withdraw;
    }
  }

  async getSendGas(retries = 3) {
    console.log(chalk.cyan('🔍 Расчет газа для отправки...'));
    
    try {
      const gas = await this.analyzeBlocks('send', 5);
      console.log(chalk.green(`✅ Получен gas для отправки: ${gas.toLocaleString()}`));
      return gas;
    } catch (error) {
      console.log(chalk.red(`❌ Ошибка расчета газа: ${error.message}`));
      console.log(chalk.yellow(`⚠️ Используем fallback значение: ${this.fallbackGas.send.toLocaleString()}`));
      return this.fallbackGas.send;
    }
  }
}

// Экспорт для использования в Python через subprocess
if (process.argv.length > 2) {
  const rpcNodes = [
    "https://cosmos-rpc.publicnode.com:443",
    "https://cosmos-rpc.polkachu.com:443",
    "https://cosmoshub-mainnet-rpc.itrocket.net"
  ];
  
  const calculator = new GasCalculator(rpcNodes);
  
  if (process.argv[2] === 'withdraw') {
    calculator.getWithdrawGas().then(gas => {
      console.log(gas); // Для Python скрипта
      process.exit(0);
    }).catch(error => {
      console.error('Error:', error.message);
      console.log(calculator.fallbackGas.withdraw);
      process.exit(1);
    });
  } else if (process.argv[2] === 'send') {
    calculator.getSendGas().then(gas => {
      console.log(gas); // Для Python скрипта
      process.exit(0);
    }).catch(error => {
      console.error('Error:', error.message);
      console.log(calculator.fallbackGas.send);
      process.exit(1);
    });
  } else {
    console.error('Usage: node gas-calculator.js [withdraw|send]');
    process.exit(1);
  }
}