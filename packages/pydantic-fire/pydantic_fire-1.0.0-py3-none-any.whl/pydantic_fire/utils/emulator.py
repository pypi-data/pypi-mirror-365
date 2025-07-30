"""
Firestore emulator integration utilities.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Callable
import os
import subprocess
import time
import json
import requests
from contextlib import contextmanager

from ..core.exceptions import SchemaError


class FirestoreEmulator:
    """
    Firestore emulator management and integration.
    """
    
    def __init__(self, 
                 project_id: str = "test-project",
                 host: str = "localhost",
                 port: int = 8080,
                 ui_port: int = 4000):
        """
        Initialize Firestore emulator manager.
        
        Args:
            project_id: Firebase project ID for testing
            host: Emulator host address
            port: Firestore emulator port
            ui_port: Emulator UI port
        """
        self.project_id = project_id
        self.host = host
        self.port = port
        self.ui_port = ui_port
        self._process = None
        self._is_running = False
    
    def start(self, 
              rules_file: Optional[str] = None,
              import_data: Optional[str] = None,
              export_on_exit: Optional[str] = None) -> bool:
        """
        Start the Firestore emulator.
        
        Args:
            rules_file: Path to Firestore rules file
            import_data: Path to data export to import
            export_on_exit: Path to export data on exit
        
        Returns:
            True if started successfully, False otherwise
        """
        if self._is_running:
            return True
        
        try:
            # Build command
            cmd = [
                "firebase", "emulators:start",
                "--only", "firestore",
                "--project", self.project_id,
                f"--port={self.port}"
            ]
            
            if rules_file and os.path.exists(rules_file):
                cmd.extend(["--rules", rules_file])
            
            if import_data and os.path.exists(import_data):
                cmd.extend(["--import", import_data])
            
            if export_on_exit:
                cmd.extend(["--export-on-exit", export_on_exit])
            
            # Start emulator process
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for emulator to start
            if self._wait_for_emulator():
                self._is_running = True
                self._setup_environment()
                return True
            else:
                self.stop()
                return False
                
        except FileNotFoundError:
            raise SchemaError("Firebase CLI not found. Please install Firebase CLI to use emulator.")
        except Exception as e:
            raise SchemaError(f"Failed to start Firestore emulator: {e}")
    
    def stop(self) -> None:
        """Stop the Firestore emulator."""
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
            
            self._process = None
        
        self._is_running = False
        self._cleanup_environment()
    
    def _wait_for_emulator(self, timeout: int = 30) -> bool:
        """
        Wait for emulator to be ready.
        
        Args:
            timeout: Maximum time to wait in seconds
        
        Returns:
            True if emulator is ready, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if emulator is responding
                response = requests.get(f"http://{self.host}:{self.port}")
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        return False
    
    def _setup_environment(self) -> None:
        """Setup environment variables for emulator."""
        os.environ["FIRESTORE_EMULATOR_HOST"] = f"{self.host}:{self.port}"
        os.environ["GCLOUD_PROJECT"] = self.project_id
    
    def _cleanup_environment(self) -> None:
        """Clean up environment variables."""
        if "FIRESTORE_EMULATOR_HOST" in os.environ:
            del os.environ["FIRESTORE_EMULATOR_HOST"]
        if "GCLOUD_PROJECT" in os.environ:
            del os.environ["GCLOUD_PROJECT"]
    
    def is_running(self) -> bool:
        """Check if emulator is running."""
        return self._is_running
    
    def clear_data(self) -> bool:
        """
        Clear all data from the emulator.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use Firebase CLI to clear data
            cmd = [
                "firebase", "firestore:delete",
                "--all-collections",
                "--project", self.project_id,
                "--yes"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def export_data(self, export_path: str) -> bool:
        """
        Export emulator data to a directory.
        
        Args:
            export_path: Path to export directory
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [
                "firebase", "emulators:export",
                export_path,
                "--project", self.project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def import_data(self, import_path: str) -> bool:
        """
        Import data into the emulator.
        
        Args:
            import_path: Path to import directory
        
        Returns:
            True if successful, False otherwise
        """
        if not self._is_running:
            return False
        
        try:
            # Stop emulator, restart with import
            self.stop()
            return self.start(import_data=import_path)
            
        except Exception:
            return False
    
    def get_ui_url(self) -> str:
        """Get the emulator UI URL."""
        return f"http://{self.host}:{self.ui_port}"
    
    def get_emulator_url(self) -> str:
        """Get the emulator endpoint URL."""
        return f"http://{self.host}:{self.port}"
    
    @contextmanager
    def running(self, **kwargs):
        """Context manager for running emulator."""
        try:
            if self.start(**kwargs):
                yield self
            else:
                raise SchemaError("Failed to start emulator")
        finally:
            self.stop()
    
    def __enter__(self):
        """Context manager entry."""
        if not self.start():
            raise SchemaError("Failed to start emulator")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


class EmulatorTestSuite:
    """
    Test suite utilities for emulator-based testing.
    """
    
    def __init__(self, emulator: FirestoreEmulator):
        """
        Initialize test suite with emulator.
        
        Args:
            emulator: FirestoreEmulator instance
        """
        self.emulator = emulator
        self._test_data_snapshots = {}
    
    def setup_test_case(self, test_name: str, test_data: Dict[str, Any]) -> None:
        """
        Setup data for a specific test case.
        
        Args:
            test_name: Name of the test case
            test_data: Test data to setup
        """
        # Clear existing data
        self.emulator.clear_data()
        
        # Store snapshot for cleanup
        self._test_data_snapshots[test_name] = test_data
        
        # Setup test data using Firebase Admin SDK or mock client
        self._setup_test_data(test_data)
    
    def teardown_test_case(self, test_name: str) -> None:
        """
        Clean up after a test case.
        
        Args:
            test_name: Name of the test case
        """
        # Clear test data
        self.emulator.clear_data()
        
        # Remove snapshot
        if test_name in self._test_data_snapshots:
            del self._test_data_snapshots[test_name]
    
    def _setup_test_data(self, test_data: Dict[str, Any]) -> None:
        """Setup test data in emulator."""
        try:
            # Try to use Firebase Admin SDK
            import firebase_admin
            from firebase_admin import firestore
            
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
            
            db = firestore.client()
            
            for collection_name, documents in test_data.items():
                if not isinstance(documents, list):
                    documents = [documents]
                
                for doc_data in documents:
                    doc_id = doc_data.get('id', f"test_{int(time.time() * 1000)}")
                    if 'id' in doc_data:
                        doc_data = doc_data.copy()
                        del doc_data['id']
                    
                    db.collection(collection_name).document(doc_id).set(doc_data)
                    
        except ImportError:
            # Fallback to google-cloud-firestore
            try:
                from google.cloud import firestore
                
                db = firestore.Client(project=self.emulator.project_id)
                
                for collection_name, documents in test_data.items():
                    if not isinstance(documents, list):
                        documents = [documents]
                    
                    for doc_data in documents:
                        doc_id = doc_data.get('id', f"test_{int(time.time() * 1000)}")
                        if 'id' in doc_data:
                            doc_data = doc_data.copy()
                            del doc_data['id']
                        
                        db.collection(collection_name).document(doc_id).set(doc_data)
                        
            except ImportError:
                raise SchemaError("Neither firebase_admin nor google-cloud-firestore is available")
    
    def create_test_snapshot(self, name: str) -> str:
        """
        Create a snapshot of current emulator data.
        
        Args:
            name: Name for the snapshot
        
        Returns:
            Path to the snapshot directory
        """
        snapshot_path = f"./test_snapshots/{name}"
        os.makedirs(snapshot_path, exist_ok=True)
        
        if self.emulator.export_data(snapshot_path):
            return snapshot_path
        else:
            raise SchemaError(f"Failed to create snapshot: {name}")
    
    def restore_test_snapshot(self, name: str) -> bool:
        """
        Restore emulator data from a snapshot.
        
        Args:
            name: Name of the snapshot to restore
        
        Returns:
            True if successful, False otherwise
        """
        snapshot_path = f"./test_snapshots/{name}"
        
        if os.path.exists(snapshot_path):
            return self.emulator.import_data(snapshot_path)
        else:
            return False


def create_emulator(project_id: str = "test-project", **kwargs) -> FirestoreEmulator:
    """
    Factory function to create a Firestore emulator.
    
    Args:
        project_id: Firebase project ID for testing
        **kwargs: Additional arguments for FirestoreEmulator
    
    Returns:
        Configured FirestoreEmulator instance
    """
    return FirestoreEmulator(project_id=project_id, **kwargs)


def create_test_suite(emulator: Optional[FirestoreEmulator] = None) -> EmulatorTestSuite:
    """
    Factory function to create an emulator test suite.
    
    Args:
        emulator: FirestoreEmulator instance (creates default if None)
    
    Returns:
        Configured EmulatorTestSuite instance
    """
    if emulator is None:
        emulator = create_emulator()
    
    return EmulatorTestSuite(emulator)
