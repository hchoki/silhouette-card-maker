"""
Thread-safe download manager with rate limiting for Scryfall API.

This module implements concurrent downloads while respecting Scryfall's
rate limit guidelines (50-100ms between requests, ~10 requests/second).
"""

import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from typing import Callable, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DownloadTask:
    """Represents a single download task."""
    index: int
    card_name: str
    card_set: str
    collector_number: str
    quantity: int
    layout: str
    original_name: str = None


class RateLimitedDownloader:
    """
    Manages concurrent downloads with rate limiting.
    
    Ensures compliance with Scryfall's rate limit guidelines:
    - 50-100ms delay between requests
    - ~10 requests per second average
    """
    
    def __init__(self, max_workers: int = 6, min_delay: float = 0.075):
        """
        Initialize the rate-limited downloader.
        
        Args:
            max_workers: Maximum number of concurrent download threads (default: 6)
            min_delay: Minimum delay between requests in seconds (default: 75ms)
        """
        self.max_workers = max_workers
        self.min_delay = min_delay
        self.last_request_time = 0
        self.lock = threading.Lock()
        self.total_downloads = 0
        self.successful_downloads = 0
        self.failed_downloads = 0
        
    def _wait_for_rate_limit(self):
        """Enforce rate limiting by waiting if necessary."""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_delay:
                sleep_time = self.min_delay - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
    
    def download_card(
        self,
        task: DownloadTask,
        fetch_function: Callable,
        front_dir: str,
        double_sided_dir: str,
        art_crop: bool
    ) -> Tuple[bool, Optional[str]]:
        """
        Download a single card with rate limiting.
        
        Args:
            task: DownloadTask containing card information
            fetch_function: Function to call for fetching the card
            front_dir: Directory for front face images
            double_sided_dir: Directory for double-sided images
            art_crop: Whether to download art crop
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            self._wait_for_rate_limit()
            
            fetch_function(
                task.index,
                task.quantity,
                task.card_name,
                task.card_set,
                task.collector_number,
                task.layout,
                front_dir,
                double_sided_dir,
                art_crop,
                task.original_name
            )
            
            with self.lock:
                self.successful_downloads += 1
            
            return True, None
            
        except Exception as e:
            with self.lock:
                self.failed_downloads += 1
            return False, str(e)
    
    def download_cards_parallel(
        self,
        tasks: List[DownloadTask],
        fetch_function: Callable,
        front_dir: str,
        double_sided_dir: str,
        art_crop: bool,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> dict:
        """
        Download multiple cards in parallel with rate limiting.
        
        Args:
            tasks: List of DownloadTask objects
            fetch_function: Function to call for fetching each card
            front_dir: Directory for front face images
            double_sided_dir: Directory for double-sided images
            art_crop: Whether to download art crop
            progress_callback: Optional callback function(completed, total)
            
        Returns:
            Dictionary with download statistics
        """
        self.total_downloads = len(tasks)
        self.successful_downloads = 0
        self.failed_downloads = 0
        
        errors = []
        
        print(f"\n🚀 Starting parallel download of {len(tasks)} cards...")
        print(f"⚙️  Workers: {self.max_workers} | Rate limit: {int(self.min_delay * 1000)}ms between requests")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(
                    self.download_card,
                    task,
                    fetch_function,
                    front_dir,
                    double_sided_dir,
                    art_crop
                ): task for task in tasks
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                success, error = future.result()
                
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, len(tasks))
                
                if not success:
                    errors.append(f"Card '{task.original_name or task.card_name}': {error}")
                    print(f"❌ Failed: {task.original_name or task.card_name}")
                else:
                    # Simple progress indicator
                    if completed % 10 == 0 or completed == len(tasks):
                        print(f"📦 Progress: {completed}/{len(tasks)} cards downloaded")
        
        elapsed_time = time.time() - start_time
        
        # Print summary
        print(f"\n✅ Download complete!")
        print(f"📊 Statistics:")
        print(f"   • Total: {self.total_downloads}")
        print(f"   • Successful: {self.successful_downloads}")
        print(f"   • Failed: {self.failed_downloads}")
        print(f"   • Time: {elapsed_time:.1f}s")
        print(f"   • Rate: {self.total_downloads / elapsed_time:.1f} cards/sec")
        
        if errors:
            print(f"\n⚠️  Errors encountered:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more")
        
        return {
            'total': self.total_downloads,
            'successful': self.successful_downloads,
            'failed': self.failed_downloads,
            'elapsed_time': elapsed_time,
            'rate': self.total_downloads / elapsed_time if elapsed_time > 0 else 0,
            'errors': errors
        }


class DownloadQueue:
    """
    Queue-based download manager for processing cards sequentially or in parallel.
    """
    
    def __init__(self):
        self.queue = Queue()
        self.tasks = []
    
    def add_task(self, task: DownloadTask):
        """Add a download task to the queue."""
        self.tasks.append(task)
    
    def get_all_tasks(self) -> List[DownloadTask]:
        """Get all queued tasks."""
        return self.tasks
    
    def clear(self):
        """Clear all tasks from the queue."""
        self.tasks.clear()
    
    def size(self) -> int:
        """Get the number of queued tasks."""
        return len(self.tasks)
