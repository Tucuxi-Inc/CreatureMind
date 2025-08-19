#!/usr/bin/env python3
"""
Server Watchdog - Monitors and manages CreatureMind server processes
"""

import os
import sys
import signal
import psutil
import time
import threading
import atexit
from typing import List, Optional

class ServerWatchdog:
    """Monitors and manages server processes"""
    
    def __init__(self):
        self.monitored_processes: List[psutil.Process] = []
        self.shutdown_event = threading.Event()
        self.monitor_thread: Optional[threading.Thread] = None
        self.register_cleanup_handlers()
    
    def register_cleanup_handlers(self):
        """Register cleanup handlers for various exit scenarios"""
        # Handle normal exit
        atexit.register(self.cleanup)
        
        # Handle signals
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Handle Ctrl+C in terminal
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down servers...")
        self.shutdown_event.set()
        self.cleanup()
        sys.exit(0)
    
    def find_server_processes(self) -> List[psutil.Process]:
        """Find all running CreatureMind server processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and isinstance(cmdline, list):
                        cmdline_str = ' '.join(cmdline)
                        
                        # Look for uvicorn processes running api.server
                        if ('uvicorn' in cmdline_str and 
                            'api.server' in cmdline_str and
                            'CreatureMind' in proc.cwd()):
                            
                            processes.append(proc)
                            print(f"📍 Found server: PID {proc.info['pid']} - {cmdline_str}")
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"⚠️ Error scanning processes: {e}")
        
        return processes
    
    def add_process(self, process: psutil.Process):
        """Add a process to be monitored"""
        if process not in self.monitored_processes:
            self.monitored_processes.append(process)
            print(f"👁️ Now monitoring: PID {process.pid}")
    
    def start_monitoring(self):
        """Start monitoring server processes"""
        # Find existing servers
        existing_servers = self.find_server_processes()
        for proc in existing_servers:
            self.add_process(proc)
        
        # Start monitor thread
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("🔍 Started process monitoring")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self.shutdown_event.is_set():
            # Clean up dead processes
            alive_processes = []
            for proc in self.monitored_processes:
                try:
                    if proc.is_running():
                        alive_processes.append(proc)
                    else:
                        print(f"💀 Process {proc.pid} has died")
                except psutil.NoSuchProcess:
                    print(f"💀 Process {proc.pid} no longer exists")
            
            self.monitored_processes = alive_processes
            
            # Check for new server processes
            current_servers = self.find_server_processes()
            for proc in current_servers:
                if proc not in self.monitored_processes:
                    self.add_process(proc)
            
            # Sleep for a bit
            time.sleep(5)
    
    def cleanup(self):
        """Clean up all monitored processes"""
        if self.shutdown_event.is_set():
            return  # Already cleaning up
        
        self.shutdown_event.set()
        
        if not self.monitored_processes:
            print("🧹 No processes to clean up")
            return
        
        print(f"🧹 Cleaning up {len(self.monitored_processes)} server processes...")
        
        # Try graceful shutdown first
        for proc in self.monitored_processes:
            try:
                if proc.is_running():
                    print(f"   Terminating PID {proc.pid}...")
                    proc.terminate()
            except psutil.NoSuchProcess:
                print(f"   PID {proc.pid} already gone")
            except Exception as e:
                print(f"   Error terminating PID {proc.pid}: {e}")
        
        # Wait a moment for graceful shutdown
        time.sleep(2)
        
        # Force kill any remaining processes
        for proc in self.monitored_processes:
            try:
                if proc.is_running():
                    print(f"   Force killing PID {proc.pid}...")
                    proc.kill()
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                print(f"   Error killing PID {proc.pid}: {e}")
        
        self.monitored_processes.clear()
        print("✅ Server cleanup complete")
    
    def status(self):
        """Print current status"""
        print(f"📊 Monitoring {len(self.monitored_processes)} processes:")
        for proc in self.monitored_processes:
            try:
                status = "Running" if proc.is_running() else "Dead"
                cpu = proc.cpu_percent()
                memory = proc.memory_info().rss / 1024 / 1024  # MB
                print(f"   PID {proc.pid}: {status} (CPU: {cpu:.1f}%, RAM: {memory:.1f}MB)")
            except Exception as e:
                print(f"   PID {proc.pid}: Error getting stats - {e}")


def main():
    """Main function for standalone usage"""
    print("🐕 CreatureMind Server Watchdog")
    print("   Monitors and cleans up server processes")
    print("   Press Ctrl+C to stop monitoring and cleanup\n")
    
    watchdog = ServerWatchdog()
    watchdog.start_monitoring()
    
    try:
        while True:
            command = input("\nCommands: 'status', 'cleanup', 'quit': ").strip().lower()
            
            if command == 'status':
                watchdog.status()
            elif command == 'cleanup':
                watchdog.cleanup()
            elif command in ['quit', 'exit', 'q']:
                break
            else:
                print("Commands: status, cleanup, quit")
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    
    watchdog.cleanup()


if __name__ == "__main__":
    main()