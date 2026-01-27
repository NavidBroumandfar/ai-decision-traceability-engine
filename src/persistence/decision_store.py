"""
File-based decision result storage.

This module provides persistent storage for DecisionResult objects using JSON files.
Each decision result is stored as a separate JSON file in the data/decisions directory.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from src.core.decision_models import DecisionResult


class FileDecisionStore:
    """
    File-based storage for decision results.
    
    Each decision result is stored as a JSON file at:
    data/decisions/{run_id}.json
    """
    
    def __init__(self, base_dir: str = "data/decisions"):
        """
        Initialize the file decision store.
        
        Args:
            base_dir: Base directory for storing decision JSON files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, result: DecisionResult) -> None:
        """
        Save a decision result to disk using atomic write.
        
        Args:
            result: The DecisionResult to save
            
        Raises:
            OSError: If the file cannot be written
            ValueError: If the result cannot be serialized
        """
        file_path = self.base_dir / f"{result.run_id}.json"
        
        # Serialize to JSON
        data = result.model_dump(mode="json")
        
        # Atomic write: write to temp file, then replace
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.base_dir,
            delete=False,
            suffix=".tmp"
        ) as tmp_file:
            json.dump(data, tmp_file, ensure_ascii=False, indent=2)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
            tmp_path = tmp_file.name
        
        # Atomic replace
        os.replace(tmp_path, file_path)
    
    def load(self, run_id: str) -> Optional[DecisionResult]:
        """
        Load a decision result from disk.
        
        Args:
            run_id: The unique identifier for the decision run
            
        Returns:
            DecisionResult if found, None otherwise
        """
        file_path = self.base_dir / f"{run_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return DecisionResult.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            # If file is corrupted, return None
            return None
    
    def exists(self, run_id: str) -> bool:
        """
        Check if a decision result exists.
        
        Args:
            run_id: The unique identifier for the decision run
            
        Returns:
            True if the decision result exists, False otherwise
        """
        file_path = self.base_dir / f"{run_id}.json"
        return file_path.exists()


if __name__ == "__main__":
    """
    Minimal smoke test for P7 persistence.
    """
    from datetime import datetime
    
    print("Running P7 persistence smoke test...")
    
    # Create a minimal valid DecisionResult
    test_result = DecisionResult(
        run_id="test-smoke-p7",
        final_decision="APPROVE",
        confidence_score=0.85,
        reason_codes=["test_reason_1", "test_reason_2"],
        created_at=datetime.now()
    )
    
    # Test save and load
    store = FileDecisionStore()
    
    # Save
    store.save(test_result)
    print(f"✓ Saved decision result: {test_result.run_id}")
    
    # Check exists
    assert store.exists(test_result.run_id), "Decision should exist after save"
    print("✓ Exists check passed")
    
    # Load
    loaded = store.load(test_result.run_id)
    assert loaded is not None, "Decision should be loadable after save"
    assert loaded.run_id == test_result.run_id, "Run ID should match"
    assert loaded.final_decision == test_result.final_decision, "Final decision should match"
    assert loaded.confidence_score == test_result.confidence_score, "Confidence score should match"
    print("✓ Load and validation passed")
    
    # Cleanup
    file_path = store.base_dir / f"{test_result.run_id}.json"
    if file_path.exists():
        file_path.unlink()
        print("✓ Cleanup completed")
    
    print("P7 persistence OK")
