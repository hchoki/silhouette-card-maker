"""
Thread-safe download manager for Scryfall API.

This module implements concurrent downloads for fetching card images.
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
    Manages concurrent downloads.
    """
    
    def __init__(self, max_workers: int = 6):
        """
        Initialize the downloader.
        
        Args:
            max_workers: Maximum number of concurrent download threads (default: 6)
        """
        self.max_workers = max_workers
        self.lock = threading.Lock()
        self.total_downloads = 0
        self.successful_downloads = 0
        self.failed_downloads = 0
    
    def download_card(
        self,
        task: DownloadTask,
        fetch_function: Callable,
        front_dir: str,
        double_sided_dir: str,
        art_crop: bool
    ) -> Tuple[bool, Optional[str]]:
        """
        Download a single card.
        
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
        Download multiple cards in parallel.
        
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
        double_sided_count = 0
        
        errors = []
        
        print(f"\nDownloading {len(tasks)} cards (workers: {self.max_workers})...")
        
        start_time = time.time()
        last_progress_print = 0
        
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
                    print(f"  ❌ {task.original_name or task.card_name}")
                else:
                    # Show each successful download with set/collector info
                    card_info = f"[{task.card_set.upper()}] #{task.collector_number}"
                    # Indicate if it's a double-sided card
                    is_double_sided = task.layout in ['transform', 'modal_dfc', 'double_faced_token', 'reversible_card']
                    if is_double_sided:
                        double_sided_count += 1
                        layout_note = " (double-sided)"
                    else:
                        layout_note = ""
                    print(f"  ✓ {task.original_name or task.card_name} {card_info}{layout_note}")
        
        elapsed_time = time.time() - start_time
        
        # Print detailed summary
        print(f"\n" + "="*60)
        print(f"Download Complete!")
        print(f"="*60)
        print(f"Total cards:       {self.total_downloads}")
        print(f"Successful:        {self.successful_downloads}")
        print(f"Failed:            {self.failed_downloads}")
        print(f"Double-sided:      {double_sided_count}")
        print(f"-" * 60)
        print(f"Time elapsed:      {elapsed_time:.1f}s")
        if elapsed_time > 0:
            print(f"Download rate:     {self.total_downloads / elapsed_time:.1f} cards/sec")
        print(f"="*60)
        
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
            'double_sided': double_sided_count,
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
