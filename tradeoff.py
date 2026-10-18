import os
import json
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import time
import psutil
from sklearn.neighbors import NearestNeighbors

# Configuration
DB_PATH = "instance/image_drive.db"
RESULT_DIR = "analysis_results"
os.makedirs(RESULT_DIR, exist_ok=True)

def get_process_memory():
    """Get current process memory usage (MB) with psutil for precision"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def get_embedding_stats():
    """Get statistics about embedding vectors"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, embedding FROM image WHERE embedding IS NOT NULL")
    results = cursor.fetchall()
    
    total_size = 0
    embedding_sizes = []
    embeddings = []
    
    for img_id, embedding_json in results:
        if embedding_json:
            size = len(embedding_json.encode('utf-8'))
            total_size += size
            embedding_sizes.append(size)
            embedding = json.loads(embedding_json)
            embeddings.append(embedding)
    
    conn.close()
    
    return {
        "count": len(results),
        "total_storage_size": total_size,
        "avg_embedding_size": np.mean(embedding_sizes) if embedding_sizes else 0,
        "embeddings": np.array(embeddings)
    }

def measure_memory_usage(func, *args, **kwargs):
    """Measure memory usage with psutil for higher precision"""
    memory_usages = []
    for _ in range(5):
        before = get_process_memory()
        func(*args, **kwargs)
        after = get_process_memory()
        memory_usages.append(after - before)
    return np.mean(memory_usages)

def search_with_loaded_embeddings(embeddings, query_vector, k=5):
    """Search using pre-loaded embedding vectors"""
    nbrs = NearestNeighbors(n_neighbors=k, metric='cosine').fit(embeddings)
    distances, indices = nbrs.kneighbors([query_vector])
    return indices, distances

def search_with_lazy_loading(query_vector, k=5):
    """Search using lazy loading (read only when needed, with strict memory release)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, embedding FROM image WHERE embedding IS NOT NULL")
    
    candidates = []
    for img_id, embedding_json in cursor:
        if embedding_json:
            embedding = np.array(json.loads(embedding_json))
            similarity = 1 - np.dot(query_vector, embedding) / (np.linalg.norm(query_vector) * np.linalg.norm(embedding))
            candidates.append((similarity, img_id))
            del embedding
    
    conn.close()
    del cursor, conn
    
    candidates.sort()
    top_k = candidates[:k]
    del candidates
    return [img_id for _, img_id in top_k], [dist for dist, _ in top_k]

def analyze_tradeoff():
    """Analyze index size vs memory trade-off with improved measurements"""
    stats = get_embedding_stats()
    print(f"Total number of embeddings: {stats['count']}")
    print(f"Total storage size: {stats['total_storage_size']/1024:.2f} KB")
    print(f"Average embedding size: {stats['avg_embedding_size']:.2f} bytes")
    
    if stats['count'] == 0:
        print("Insufficient embedding data for analysis")
        return
    
    query_vector = np.random.rand(*stats['embeddings'][0].shape)
    
    print("\nMeasuring memory usage...")
    mem_loaded_before = get_process_memory()
    search_with_loaded_embeddings(stats['embeddings'], query_vector)
    mem_loaded_after = get_process_memory()
    mem_loaded = mem_loaded_after - mem_loaded_before
    
    mem_lazy_before = get_process_memory()
    search_with_lazy_loading(query_vector)
    mem_lazy_after = get_process_memory()
    mem_lazy = mem_lazy_after - mem_lazy_before

    print("Measuring execution time...")
    # 测量预加载策略的执行时间
    time_loaded_list = []
    for _ in range(10): 
        start = time.perf_counter()
        search_with_loaded_embeddings(stats['embeddings'], query_vector)
        end = time.perf_counter()
        time_loaded_list.append((end - start) * 1000) # Transform into ms
    time_loaded_avg = np.mean(time_loaded_list) # Average

    time_lazy_list = []
    for _ in range(10): 
        start = time.perf_counter()
        search_with_lazy_loading(query_vector)
        end = time.perf_counter()
        time_lazy_list.append((end - start) * 1000) # Transform into ms
    time_lazy_avg = np.mean(time_lazy_list)# Average

    print("\nPerformance Comparison:")
    print(f"Pre-loaded Strategy - Memory Usage: {mem_loaded:.2f} MB, Average Execution Time: {time_loaded_avg:.2f} ms")
    print(f"Lazy Loading Strategy - Memory Usage: {mem_lazy:.2f} MB, Average Execution Time: {time_lazy_avg:.2f} ms")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    strategies = ['Pre-loaded', 'Lazy Loading']
    
    # 内存对比图
    memory_usages = [mem_loaded, mem_lazy]
    ax1.bar(strategies, memory_usages, color=['blue', 'green'])
    ax1.set_title('Memory Usage Comparison (MB)')
    ax1.set_ylabel('Memory Usage (MB)')
    
    # 执行时间对比图
    execution_times = [time_loaded_avg, time_lazy_avg]
    ax2.bar(strategies, execution_times, color=['red', 'orange'])
    ax2.set_title('Average Execution Time Comparison (ms)')
    ax2.set_ylabel('Average Execution Time (ms)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULT_DIR, 'memory_vs_time.png'))
    print(f"\nChart saved to {os.path.join(RESULT_DIR, 'memory_vs_time.png')}")
    


    with open(os.path.join(RESULT_DIR, 'analysis_report.txt'), 'w') as f:
        f.write("Index Size vs Memory Trade-off Analysis Report\n")
        f.write("============================================\n\n")
        f.write(f"Total number of embeddings: {stats['count']}\n")
        f.write(f"Total storage size: {stats['total_storage_size']/1024:.2f} KB\n")
        f.write(f"Average embedding size: {stats['avg_embedding_size']:.2f} bytes\n\n")
        
        f.write("Performance Comparison:\n")
        f.write(f"Pre-loaded Strategy - Memory Usage: {mem_loaded:.2f} MB, Average Execution Time: {time_loaded_avg:.2f} ms\n")
        f.write(f"Lazy Loading Strategy - Memory Usage: {mem_lazy:.2f} MB, Average Execution Time: {time_lazy_avg:.2f} ms\n\n")
        
        # f.write("Conclusions:\n")
        # if mem_loaded > mem_lazy:
        #     f.write("1. The pre-loaded strategy uses more memory but has shorter execution time.\n")
        # else:
        #     f.write("1. The lazy loading strategy uses less memory but has longer execution time.\n")
            
        # f.write("2. Memory usage grows linearly with index size.\n")
        # f.write("3. For large-scale deployments, consider using a dedicated vector database (such as FAISS) to balance memory and performance.\n")

if __name__ == "__main__":
    analyze_tradeoff()