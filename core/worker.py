"""
Worker module for handling concurrent survey automation tasks
"""

import os
import queue
import threading
import traceback
from typing import Dict, List, Tuple, Optional, Callable
import pandas as pd

from core.automation import SurveyAutomation
from core.utils.pageUtils import SurveyConfig
from utils.dataGenerator import DataGenerator
from utils.logger import get_logger

logger = get_logger(__name__)


class SharedState:
    """Shared state for progress tracking across threads"""
    
    def __init__(self, total_tasks: int = 0):
        self.lock = threading.Lock()
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        self.update_callback = None
    
    def task_completed(self, success: bool = True):
        """Update the task completion count and notify callback"""
        with self.lock:
            self.completed_tasks += 1
            if self.update_callback:
                progress = (self.completed_tasks / self.total_tasks) * 100 if self.total_tasks > 0 else 0
                self.update_callback(progress, self.completed_tasks, self.total_tasks)
    
    def get_progress(self) -> float:
        """Return current progress percentage"""
        with self.lock:
            return (self.completed_tasks / self.total_tasks) * 100 if self.total_tasks > 0 else 0


def worker(task_queue: queue.Queue, results: List, shared_state: SharedState, submit_form: bool = False, location: str = "Chatswood"):
    """Worker thread function to process tasks from queue"""
    while not task_queue.empty():
        try:
            row_data = task_queue.get(block=False)
            print(f"location: {row_data['location']}, date: {row_data['date']}")
            automator = SurveyAutomation(row_data, submit=submit_form, location=location)
            success = automator.fill_survey()
            
            results.append({
                'location': row_data['location'],
                'date': row_data['date'],
                'success': success
            })

            shared_state.task_completed(success)
            task_queue.task_done()

        except queue.Empty:
            break
        except Exception as e:
            logger.error(f"Worker thread error: {e}")
            if 'row_data' in locals():
                results.append({
                    'location': row_data['location'],
                    'date': row_data['date'],
                    'success': False,
                    'error': str(e)
                })
                shared_state.task_completed(False)
            task_queue.task_done()


def excel_mode(excel_file_path: str, num_threads: int = 1, submit_form: bool = False, 
               progress_callback: Optional[Callable] = None) -> Tuple[int, int]:
    """Process Excel data and start worker threads"""
    try:
        logger.info(f"Excel Mode - Threads: {num_threads}, Submit: {submit_form}")

        if not os.path.exists(excel_file_path):
            logger.error(f"Excel file not found: {excel_file_path}")
            return 0, 0

        # Read and validate Excel data
        df = pd.read_excel(excel_file_path)
        
        if df.empty:
            logger.error("Excel file is empty")
            return 0, 0
        
        # Check required columns
        config = SurveyConfig()
        missing_columns = [col for col in config.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {', '.join(missing_columns)}")
            return 0, 0
        
        data_list = df.to_dict('records')
        logger.info(f"Processing {len(data_list)} records")

        return _process_tasks(data_list, num_threads, submit_form, progress_callback)
        
    except Exception as e:
        logger.error(f"Excel mode error: {e}")
        logger.error(traceback.format_exc())
        return 0, 0


def agent_mode(num_runs: int = 1, num_threads: int = 1, submit_form: bool = False, location: str = "Chatswood",
               progress_callback: Optional[Callable] = None) -> Tuple[int, int]:
    """Generate random survey data and submit automatically"""
    try:
        logger.info(f"Agent Mode - Runs: {num_runs}, Threads: {num_threads}, Submit: {submit_form}")
        
        # Generate random data
        data_list = [DataGenerator.generate_survey_data() for _ in range(num_runs)]
        
        return _process_tasks(data_list, num_threads, submit_form, location, progress_callback)
        
    except Exception as e:
        logger.error(f"Agent mode error: {e}")
        logger.error(traceback.format_exc())
        return 0, num_runs


def _process_tasks(data_list: List[Dict], num_threads: int, submit_form: bool,
                   location: str, progress_callback: Optional[Callable]) -> Tuple[int, int]:
    """Common function to process tasks with multiple threads"""
    shared_state = SharedState(total_tasks=len(data_list))
    if progress_callback:
        shared_state.update_callback = progress_callback
    
    task_queue = queue.Queue()
    for item in data_list:
        task_queue.put(item)
    
    results = []
    threads = []
    
    # Create and start worker threads
    for _ in range(min(num_threads, len(data_list))):  # Don't create more threads than tasks
        thread = threading.Thread(target=worker, args=(task_queue, results, shared_state, submit_form, location))
        thread.start()
        threads.append(thread)
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Calculate results
    successes = sum(1 for r in results if r['success'])
    failures = len(results) - successes
    
    logger.info(f"Task completed! Success: {successes}, Failures: {failures}")
    
    if failures > 0:
        logger.warning("Failed tasks:")
        for r in results:
            if not r['success']:
                logger.warning(f"  Location: {r['location']}, Date: {r['date']}, Error: {r.get('error', 'Unknown')}")
    
    return successes, failures