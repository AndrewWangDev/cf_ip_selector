import threading
import time
from concurrent.futures import ThreadPoolExecutor
from .ip_manager import load_cidrs, generate_random_ips
from .speed_tester import test_connect_latency

class SpeedTestController:
    def __init__(self, update_callback=None, finish_callback=None):
        self.update_callback = update_callback  # Called with (stats dict)
        self.finish_callback = finish_callback  # Called when finished
        
        self.is_running = False
        self.is_paused = False
        self.stop_event = threading.Event()
        
        self.all_ips = []
        self.results = [] # List of dicts: {'ip': str, 'latency': float}
        self.total_count = 0
        self.tested_count = 0
        
        self.executor = None
        
    def start_test(self, file_path="ip.txt", max_workers=50, ip_count=200):
        if self.is_running:
            return

        self.is_running = True
        self.is_paused = False
        self.stop_event.clear()
        
        # Load IPs in a separate thread to not freeze UI
        threading.Thread(target=self._prepare_and_run, args=(file_path, max_workers, ip_count), daemon=True).start()

    def _prepare_and_run(self, file_path, max_workers, ip_count):
        try:
            cidrs = load_cidrs(file_path)
        except Exception:
            cidrs = []
            
        if not cidrs:
             if self.finish_callback:
                self.finish_callback(error="CIDR file not found or empty.")
             self.is_running = False
             return
             
        self.all_ips = generate_random_ips(cidrs, total_count=ip_count)
        self.total_count = len(self.all_ips)
        self.tested_count = 0
        self.results = []
        
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Semaphore to control the submission rate, allowing pause to work
        sem = threading.Semaphore(max_workers + 10)

        def done_cb(fut):
            sem.release()
            
        for ip in self.all_ips:
            if self.stop_event.is_set():
                break
                
            while self.is_paused:
                time.sleep(0.1)
                if self.stop_event.is_set():
                    break
            
            sem.acquire()
            fut = self.executor.submit(self._run_single_test, ip)
            fut.add_done_callback(done_cb)
            
        # Wait for all tasks to complete
        self.executor.shutdown(wait=True)
        self.is_running = False
        
        if self.finish_callback:
            if self.stop_event.is_set():
                 self.finish_callback(error="Stopped by user")
            else:
                 self.finish_callback(error=None)

    def _run_single_test(self, ip):
        if self.stop_event.is_set():
            return
            
        latency = test_connect_latency(ip)
        
        with threading.Lock():
            self.tested_count += 1
            
            if latency is not None:
                result = {'ip': ip, 'latency': latency}
                self.results.append(result)
                # Keep sorted
                self.results.sort(key=lambda x: x['latency'])
                
            # Notify UI
            if self.update_callback:
                top_5 = self.results[:5]
                stats = {
                    'total': self.total_count,
                    'tested': self.tested_count,
                    'top_results': top_5
                }
                self.update_callback(stats)

    def pause_test(self):
        self.is_paused = not self.is_paused
        return self.is_paused

    def stop_test(self):
        self.stop_event.set()
        # We don't force kill threads, but we stop submitting.
        # Threads in flight will finish.
