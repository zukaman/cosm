// js/health-check.js - Полная версия
import axios from 'axios';
import chalk from 'chalk';
import { RPCClient } from './rpc-client.js';

class HealthChecker {
  constructor(rpcEndpoints) {
    this.rpcEndpoints = rpcEndpoints;
    this.results = [];
  }

  async checkSingleEndpoint(url) {
    const result = {
      url,
      status: 'unknown',
      responseTime: 0,
      blockHeight: 0,
      error: null,
      details: {}
    };

    const startTime = Date.now();

    try {
      const statusResponse = await axios.get(`${url}/status`, { 
        timeout: 10000,
        headers: { 'User-Agent': 'Cosmos-Health-Check/1.0' }
      });
      
      result.responseTime = Date.now() - startTime;
      
      if (statusResponse.status === 200) {
        result.status = 'healthy';
        
        if (statusResponse.data?.result?.sync_info) {
          const syncInfo = statusResponse.data.result.sync_info;
          result.blockHeight = parseInt(syncInfo.latest_block_height);
          result.details = {
            network: statusResponse.data.result.node_info?.network,
            version: statusResponse.data.result.node_info?.version,
            catching_up: syncInfo.catching_up,
            latest_block_time: syncInfo.latest_block_time
          };
        }
      } else {
        result.status = 'unhealthy';
        result.error = `HTTP ${statusResponse.status}`;
      }
      
    } catch (error) {
      result.status = 'error';
      result.error = error.message;
      result.responseTime = Date.now() - startTime;
      
      if (error.code === 'ENOTFOUND') result.error = 'DNS resolution failed';
      else if (error.code === 'ECONNREFUSED') result.error = 'Connection refused';
      else if (error.code === 'ETIMEDOUT') result.error = 'Connection timeout';
    }

    return result;
  }

  async checkAllEndpoints() {
    console.log(chalk.blue('🏥 Проверка состояния RPC узлов...'));
    console.log(chalk.gray(`Проверяем ${this.rpcEndpoints.length} узлов...\n`));

    const promises = this.rpcEndpoints.map(url => this.checkSingleEndpoint(url));
    this.results = await Promise.all(promises);
    return this.results;
  }

  printResults() {
    console.log(chalk.cyan('\n📊 Результаты проверки:'));
    console.log('='.repeat(80));

    let healthyCount = 0;
    let totalResponseTime = 0;
    let maxBlockHeight = 0;

    this.results.forEach((result, index) => {
      const status = result.status === 'healthy' ? 
        chalk.green('✅ ЗДОРОВ') : 
        result.status === 'error' ? 
          chalk.red('❌ ОШИБКА') : 
          chalk.yellow('⚠️  ПРОБЛЕМА');
      
      console.log(chalk.white(`\n${index + 1}. ${result.url}`));
      console.log(`   Статус: ${status}`);
      console.log(chalk.gray(`   Время отклика: ${result.responseTime}ms`));
      
      if (result.status === 'healthy') {
        healthyCount++;
        totalResponseTime += result.responseTime;
        maxBlockHeight = Math.max(maxBlockHeight, result.blockHeight);
        
        console.log(chalk.blue(`   Высота блока: ${result.blockHeight.toLocaleString()}`));
        
        if (result.details.network) {
          console.log(chalk.gray(`   Сеть: ${result.details.network}`));
        }
      } else {
        console.log(chalk.red(`   Ошибка: ${result.error}`));
      }
    });

    const healthPercentage = Math.round((healthyCount / this.results.length) * 100);
    console.log(chalk.cyan('\n📈 Общая статистика:'));
    console.log(chalk.white(`   Здоровых узлов: ${healthyCount}/${this.results.length}`));
    
    if (healthyCount > 0) {
      const avgResponseTime = Math.round(totalResponseTime / healthyCount);
      console.log(chalk.white(`   Среднее время отклика: ${avgResponseTime}ms`));
      console.log(chalk.white(`   Максимальная высота блока: ${maxBlockHeight.toLocaleString()}`));
    }
    
    const healthColor = healthPercentage >= 80 ? chalk.green : 
                       healthPercentage >= 50 ? chalk.yellow : chalk.red;
    console.log(healthColor(`   Процент доступности: ${healthPercentage}%`));

    if (healthyCount === 0) {
      console.log(chalk.red('\n🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Все RPC узлы недоступны!'));
    } else if (healthyCount < this.results.length / 2) {
      console.log(chalk.yellow('\n⚠️  ВНИМАНИЕ: Более половины RPC узлов недоступны'));
    } else {
      console.log(chalk.green('\n✅ Система RPC узлов работает стабильно'));
    }

    return {
      healthy: healthyCount,
      total: this.results.length,
      percentage: healthPercentage,
      avgResponseTime: healthyCount > 0 ? Math.round(totalResponseTime / healthyCount) : 0,
      maxBlockHeight
    };
  }
}

// Запуск если вызван напрямую
if (import.meta.url === `file://${process.argv[1]}`) {
  const rpcEndpoints = [
    "https://cosmos-rpc.publicnode.com:443",
    "https://cosmos-rpc.polkachu.com:443",
    "https://cosmoshub-mainnet-rpc.itrocket.net"
  ];

  const checker = new HealthChecker(rpcEndpoints);
  
  checker.checkAllEndpoints()
    .then(() => checker.printResults())
    .catch(error => {
      console.error(chalk.red('❌ Ошибка проверки здоровья:'), error.message);
      process.exit(1);
    });
}

export { HealthChecker };