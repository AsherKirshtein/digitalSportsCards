from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import sys

class SafeCounter:
    def __init__(self, initial_value=0):
        self.value = initial_value
        self._lock = threading.Lock()

    def decrement(self):
        with self._lock:
            self.value -= 1

    def get_value(self):
        with self._lock:
            return self.value

def process_link(link, counter):
    # Your link processing logic here
    # ...
    time.sleep(0.1)  # Simulate processing time

    counter.decrement()

def print_progress_bar(total, counter):
    while counter.get_value() > 0:
        completed = total - counter.get_value()
        percent = (completed / total) * 100
        bar = '#' * int(percent // 2) + '-' * (50 - int(percent // 2))
        print(f"\r[{bar}] {percent:.2f}%", end='')
        time.sleep(0.5)
    print("\r[{}] 100.00%".format('#' * 50))  # Complete the bar

def main():
    total_links = 1000
    counter = SafeCounter(total_links)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_link, link, counter) for link in range(total_links)]

        # Start a thread for printing the progress bar
        threading.Thread(target=print_progress_bar, args=(total_links, counter), daemon=True).start()

        # Wait for all tasks to complete
        for future in as_completed(futures):
            pass

    print("\nProcessing complete.")

if __name__ == "__main__":
    main()
