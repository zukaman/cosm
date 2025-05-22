// js/rpc-client.js
// Умный клиент для работы с RPC узлами

import axios from 'axios';
import chalk from 'chalk';

export class RPCClient {
  constructor(endpoints, options = {}) {
    this.endpoints = endpoints.map(url => ({
      url,
      healthy: true,
      lastCheck: 0,
      responseTime: 0,
      failures: 0
    }));
    
    this.options = {
      timeout: options.timeout || 30000,
      maxRetries: options.maxRetries || 3,
      healthCheckInterval: options.healthCheckInterval || 300000, // 5 минут
      maxFailures: options.maxFailures || 3,
      ...options
    };
    
    this.currentIndex = 0;
    this.stats = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0
    };
    
    // Запускаем периодическую проверку здоровья
    this.startHealthChecks();
  }

  startHealthChecks() {
    setInterval(() => {
      this.checkAllEndpointsHealth();
    }, this.options.healthCheckInterval);
  }

  async checkAllEndpointsHealth() {
    console.log(chalk.blue('🏥 Проверка состояния RPC узлов...'));
    
    const healthPromises = this.endpoints.map(async (endpoint) => {
      const startTime = Date.now();
      try {
        const response = await axios.get(`${endpoint.url}/status`, {
          timeout: 5000
        });
        
        const responseTime = Date.now() - startTime;
        endpoint.healthy = response.status === 200;
        endpoint.responseTime = responseTime;
        endpoint.lastCheck = Date.now();
        endpoint.failures = 0;
        
        console.log(chalk.green(`✅ ${endpoint.url} - ${responseTime}ms`));
      } catch (error) {
        endpoint.healthy = false;
        endpoint.failures++;
        endpoint.lastCheck = Date.now();
        
        console.log(chalk.red(`❌ ${endpoint.url} - ${error.message}`));
      }
      
      return endpoint;
    });
    
    await Promise.all(healthPromises);
    
    const healthyCount = this.endpoints.filter(e => e.healthy).length;
    console.log(chalk.cyan(`📊 Здоровых узлов: ${healthyCount}/${this.endpoints.length}`));
  }

  getHealthyEndpoints() {
    return this.endpoints.filter(endpoint => 
      endpoint.healthy && 
      endpoint.failures < this.options.maxFailures
    );
  }

  getBestEndpoint() {
    const healthy = this.getHealthyEndpoints();
    
    if (healthy.length === 0) {
      // Если нет здоровых узлов, используем любой
      console.log(chalk.yellow('⚠️ Нет здоровых RPC узлов, используем первый доступный'));
      return this.endpoints[0];
    }
    
    // Сортируем по времени отклика
    healthy.sort((a, b) => a.responseTime - b.responseTime);
    return healthy[0];
  }

  getRandomHealthyEndpoint() {
    const healthy = this.getHealthyEndpoints();
    
    if (healthy.length === 0) {
      return this.endpoints[Math.floor(Math.random() * this.endpoints.length)];
    }
    
    return healthy[Math.floor(Math.random() * healthy.length)];
  }

  async makeRequest(path, options = {}) {
    const method = options.method || 'GET';
    const data = options.data;
    let lastError;
    
    this.stats.totalRequests++;
    
    for (let attempt = 0; attempt < this.options.maxRetries; attempt++) {
      const endpoint = options.preferFast ? this.getBestEndpoint() : this.getRandomHealthyEndpoint();
      const url = `${endpoint.url}${path}`;
      
      try {
        const startTime = Date.now();
        
        const config = {
          method,
          url,
          timeout: this.options.timeout,
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Cosmos-Automation/1.0'
          }
        };
        
        if (data) {
          config.data = data;
        }
        
        const response = await axios(config);
        
        const responseTime = Date.now() - startTime;
        endpoint.responseTime = (endpoint.responseTime + responseTime) / 2; // Скользящее среднее
        
        this.stats.successfulRequests++;
        this.updateAverageResponseTime(responseTime);
        
        return response.data;
        
      } catch (error) {
        lastError = error;
        endpoint.failures++;
        
        if (endpoint.failures >= this.options.maxFailures) {
          endpoint.healthy = false;
          console.log(chalk.red(`🚫 Узел ${endpoint.url} помечен как нездоровый`));
        }
        
        console.log(chalk.yellow(`⚠️ Попытка ${attempt + 1}/${this.options.maxRetries} неудачна для ${endpoint.url}: ${error.message}`));
        
        if (attempt < this.options.maxRetries - 1) {
          await this.sleep(1000 * (attempt + 1)); // Экспоненциальная задержка
        }
      }
    }
    
    this.stats.failedRequests++;
    throw new Error(`Все ${this.options.maxRetries} попыток неудачны. Последняя ошибка: ${lastError?.message}`);
  }

  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  updateAverageResponseTime(responseTime) {
    const total = this.stats.totalRequests;
    this.stats.averageResponseTime = 
      (this.stats.averageResponseTime * (total - 1) + responseTime) / total;
  }

  // Специализированные методы для Cosmos API
  async getBalance(address, denom = 'uatom') {
    try {
      const data = await this.makeRequest(`/cosmos/bank/v1beta1/balances/${address}`);
      const balance = data.balances?.find(b => b.denom === denom);
      return balance ? parseInt(balance.amount) : 0;
    } catch (error) {
      console.log(chalk.red(`❌ Ошибка получения баланса: ${error.message}`));
      return 0;
    }
  }

  async getRewards(delegatorAddress) {
    try {
      const data = await this.makeRequest(`/cosmos/distribution/v1beta1/delegators/${delegatorAddress}/rewards`);
      const atomRewards = data.total?.find(reward => reward.denom === 'uatom');
      return atomRewards ? parseFloat(atomRewards.amount) : 0;
    } catch (error) {
      console.log(chalk.red(`❌ Ошибка получения наград: ${error.message}`));
      return 0;
    }
  }

  async getTransaction(txHash) {
    try {
      const data = await this.makeRequest(`/cosmos/tx/v1beta1/txs/${txHash}`);
      return data.tx_response;
    } catch (error) {
      if (error.response?.status === 404) {
        return null; // Транзакция не найдена
      }
      throw error;
    }
  }

  async getBlock(height) {
    try {
      const data = await this.makeRequest(`/cosmos/base/tendermint/v1beta1/blocks/${height}`);
      return data.block;
    } catch (error) {
      console.log(chalk.red(`❌ Ошибка получения блока ${height}: ${error.message}`));
      return null;
    }
  }

  async getLatestBlock() {
    try {
      const data = await this.makeRequest('/cosmos/base/tendermint/v1beta1/blocks/latest');
      return data.block;
    } catch (error) {
      console.log(chalk.red(`❌ Ошибка получения последнего блока: ${error.message}`));
      return null;
    }
  }

  getStats() {
    const successRate = this.stats.totalRequests > 0 
      ? (this.stats.successfulRequests / this.stats.totalRequests * 100).toFixed(2)
      : 0;
    
    return {
      ...this.stats,
      successRate: `${successRate}%`,
      averageResponseTime: `${Math.round(this.stats.averageResponseTime)}ms`,
      healthyEndpoints: this.getHealthyEndpoints().length,
      totalEndpoints: this.endpoints.length
    };
  }

  printStats() {
    const stats = this.getStats();
    console.log(chalk.cyan('📊 Статистика RPC клиента:'));
    console.log(chalk.white(`  Всего запросов: ${stats.totalRequests}`));
    console.log(chalk.green(`  Успешных: ${stats.successfulRequests}`));
    console.log(chalk.red(`  Неудачных: ${stats.failedRequests}`));
    console.log(chalk.blue(`  Успешность: ${stats.successRate}`));
    console.log(chalk.yellow(`  Среднее время отклика: ${stats.averageResponseTime}`));
    console.log(chalk.cyan(`  Здоровых узлов: ${stats.healthyEndpoints}/${stats.totalEndpoints}`));
  }

  async testAllEndpoints() {
    console.log(chalk.blue('🧪 Тестирование всех RPC узлов...'));
    
    for (const endpoint of this.endpoints) {
      const startTime = Date.now();
      try {
        await axios.get(`${endpoint.url}/status`, { timeout: 10000 });
        const responseTime = Date.now() - startTime;
        console.log(chalk.green(`✅ ${endpoint.url} - ${responseTime}ms - OK`));
      } catch (error) {
        console.log(chalk.red(`❌ ${endpoint.url} - FAILED: ${error.message}`));
      }
    }
  }
}