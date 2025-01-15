import pytest
import asyncio
import aiohttp
import time
from datetime import datetime

async def make_request(session, url, auth_headers, request_num):
    try:
        async with session.post(url, headers=auth_headers) as response:
            data = await response.json()
            return {
                'request_num': request_num,
                'status': response.status,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {
            'request_num': request_num,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

async def stress_test_endpoint(base_url, auth_headers, num_requests=100, concurrent_requests=10):
    """
    Esegue test di stress su un endpoint
    
    Args:
        base_url: URL dell'endpoint da testare
        auth_headers: Headers di autenticazione
        num_requests: Numero totale di richieste
        concurrent_requests: Numero di richieste concorrenti
    """
    results = []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            task = make_request(session, base_url, auth_headers, i)
            tasks.append(task)
            
            if len(tasks) >= concurrent_requests:
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                tasks = []
                
        if tasks:
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
    
    return results

def analyze_results(results):
    """Analizza i risultati del test di stress"""
    status_counts = {}
    response_times = []
    rate_limit_hits = 0
    
    for i in range(len(results)):
        status = results[i]['status']
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if i > 0:
            prev_time = datetime.fromisoformat(results[i-1]['timestamp'])
            curr_time = datetime.fromisoformat(results[i]['timestamp'])
            response_times.append((curr_time - prev_time).total_seconds())
        
        if status == 429:  # Rate limit exceeded
            rate_limit_hits += 1
    
    return {
        'status_counts': status_counts,
        'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
        'rate_limit_hits': rate_limit_hits,
        'success_rate': (status_counts.get(200, 0) / len(results)) * 100
    }

@pytest.mark.asyncio
async def test_auth_rate_limiting():
    """Test di stress per il rate limiting dell'autenticazione"""
    base_url = 'http://localhost:5000/api/auth/login'
    auth_headers = {'Content-Type': 'application/json'}
    
    results = await stress_test_endpoint(
        base_url=base_url,
        auth_headers=auth_headers,
        num_requests=50,
        concurrent_requests=5
    )
    
    analysis = analyze_results(results)
    
    # Verifica che il rate limiting funzioni
    assert analysis['rate_limit_hits'] > 0, "Il rate limiting non sta bloccando le richieste"
    assert analysis['success_rate'] < 100, "Tutte le richieste sono passate - il rate limiting non funziona"
    
    print("\nRisultati test di stress autenticazione:")
    print(f"Totale richieste: {len(results)}")
    print(f"Rate limit hits: {analysis['rate_limit_hits']}")
    print(f"Success rate: {analysis['success_rate']:.2f}%")
    print(f"Tempo di risposta medio: {analysis['avg_response_time']:.3f}s")
    print(f"Status codes: {analysis['status_counts']}")

@pytest.mark.asyncio
async def test_api_rate_limiting():
    """Test di stress per il rate limiting delle API"""
    base_url = 'http://localhost:5000/api/interactions'
    auth_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token'  # Sostituire con un token valido
    }
    
    results = await stress_test_endpoint(
        base_url=base_url,
        auth_headers=auth_headers,
        num_requests=30,
        concurrent_requests=3
    )
    
    analysis = analyze_results(results)
    
    print("\nRisultati test di stress API:")
    print(f"Totale richieste: {len(results)}")
    print(f"Rate limit hits: {analysis['rate_limit_hits']}")
    print(f"Success rate: {analysis['success_rate']:.2f}%")
    print(f"Tempo di risposta medio: {analysis['avg_response_time']:.3f}s")
    print(f"Status codes: {analysis['status_counts']}")