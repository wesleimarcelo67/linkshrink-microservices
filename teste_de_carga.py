import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stress_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def flood_request(url, request_id):
    """Executa uma requisição individual e retorna o resultado"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=15)
        duration = time.time() - start_time
        
        result = {
            'id': request_id,
            'status': response.status_code,
            'duration': duration,
            'success': True,
            'error': None
        }
        
        logger.info(f"✅ Requisição {request_id}: HTTP {response.status_code} ({duration:.2f}s)")
        return result
        
    except requests.exceptions.Timeout:
        error_msg = "Timeout"
        logger.warning(f"⏰ Requisição {request_id}: Timeout")
    except requests.exceptions.ConnectionError:
        error_msg = "Connection Error"
        logger.warning(f"🔌 Requisição {request_id}: Connection Error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Request Error: {str(e)}"
        logger.warning(f"❌ Requisição {request_id}: {error_msg}")
    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        logger.error(f"💥 Requisição {request_id}: {error_msg}")
    
    return {
        'id': request_id,
        'status': None,
        'duration': None,
        'success': False,
        'error': error_msg
    }

def run_stress_test():
    """Executa o teste de estresse completo"""
    # Configurações
    TARGET_URL = "https://linkshrink.projetotcc.online"
    TOTAL_REQUESTS = 5000  # Número total de requisições
    MAX_WORKERS = 200      # Número de threads simultâneas
    BATCH_SIZE = 1000       # Tamanho do lote para logging
    
    logger.info("🚀 INICIANDO TESTE DE ESTRESSE")
    logger.info(f"🎯 Target: {TARGET_URL}")
    logger.info(f"📊 Total de requisições: {TOTAL_REQUESTS}")
    logger.info(f"⚡ Threads simultâneas: {MAX_WORKERS}")
    logger.info("-" * 50)
    
    start_time = datetime.now()
    results = []
    successful_requests = 0
    failed_requests = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submete todas as tarefas
        future_to_id = {
            executor.submit(flood_request, TARGET_URL, i): i 
            for i in range(TOTAL_REQUESTS)
        }
        
        # Processa os resultados conforme ficam prontos
        for batch_num, future in enumerate(as_completed(future_to_id), 1):
            try:
                result = future.result()
                results.append(result)
                
                if result['success']:
                    successful_requests += 1
                else:
                    failed_requests += 1
                
                # Log a cada lote de requisições
                if batch_num % BATCH_SIZE == 0 or batch_num == TOTAL_REQUESTS:
                    progress = (batch_num / TOTAL_REQUESTS) * 100
                    logger.info(
                        f"📈 Progresso: {batch_num}/{TOTAL_REQUESTS} "
                        f"({progress:.1f}%) | "
                        f"✅ Sucessos: {successful_requests} | "
                        f"❌ Falhas: {failed_requests}"
                    )
                    
            except Exception as e:
                logger.error(f"💣 Erro ao processar resultado: {str(e)}")
                failed_requests += 1
    
    # Cálculo das estatísticas finais
    total_time = (datetime.now() - start_time).total_seconds()
    avg_duration = sum(r['duration'] for r in results if r['duration']) / max(successful_requests, 1)
    
    # Análise detalhada dos status HTTP
    status_codes = {}
    for result in results:
        if result['status']:
            status_codes[result['status']] = status_codes.get(result['status'], 0) + 1
    
    # Análise de erros
    error_types = {}
    for result in results:
        if result['error']:
            error_types[result['error']] = error_types.get(result['error'], 0) + 1
    
    # Relatório final
    logger.info("=" * 60)
    logger.info("🎯 RELATÓRIO FINAL DO TESTE")
    logger.info("=" * 60)
    logger.info(f"⏰ Tempo total de execução: {total_time:.2f} segundos")
    logger.info(f"📊 Requisições por segundo: {TOTAL_REQUESTS/total_time:.2f}")
    logger.info(f"✅ Requisições bem-sucedidas: {successful_requests}")
    logger.info(f"❌ Requisições com falha: {failed_requests}")
    logger.info(f"📈 Taxa de sucesso: {(successful_requests/TOTAL_REQUESTS)*100:.1f}%")
    logger.info(f"⏱️  Tempo médio por requisição: {avg_duration:.3f} segundos")
    
    # Detalhes dos status HTTP
    if status_codes:
        logger.info("\n📋 Códigos de Status HTTP:")
        for code, count in sorted(status_codes.items()):
            logger.info(f"   HTTP {code}: {count} requisições")
    
    # Detalhes dos erros
    if error_types:
        logger.info("\n🔍 Tipos de Erro:")
        for error, count in error_types.items():
            logger.info(f"   {count}x {error}")
    
    # Estatísticas de tempo
    durations = [r['duration'] for r in results if r['duration']]
    if durations:
        min_dur = min(durations)
        max_dur = max(durations)
        logger.info(f"\n⏱️  Estatísticas de Tempo:")
        logger.info(f"   Mínimo: {min_dur:.3f}s")
        logger.info(f"   Máximo: {max_dur:.3f}s")
        logger.info(f"   Médio: {avg_duration:.3f}s")
    
    logger.info("=" * 60)
    logger.info("🏁 Teste concluído!")
    
    return results

if __name__ == "__main__":
    # Executa o teste
    results = run_stress_test()
    
    # Salva resultados em CSV para análise posterior
    try:
        import csv
        with open('stress_test_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'status', 'duration', 'success', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        logger.info("💾 Resultados salvos em stress_test_results.csv")
        
    except Exception as e:
        logger.error(f"Erro ao salvar CSV: {e}")