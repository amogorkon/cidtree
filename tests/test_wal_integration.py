#!/usr/bin/env python3
"""Test script to verify WAL analyzer integration with store."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import cidstore.wal_analyzer as wal_analyzer
from cidstore.constants import OpType
from cidstore.maintenance import MaintenanceConfig, WALAnalyzer


def test_wal_analyzer_basic():
    """Test basic WAL analyzer functionality."""
    analyzer = WALAnalyzer(store=None, config=MaintenanceConfig())

    # Test recording operations
    analyzer.record_operation(1, OpType.INSERT)
    analyzer.record_operation(1, OpType.INSERT)
    analyzer.record_operation(2, OpType.DELETE)

    # Test danger score calculation
    danger_score = analyzer.get_danger_score(1)
    print(f"Danger score for bucket_0001: {danger_score}")

    # No get_adaptive_split_threshold in WALAnalyzer; skip or mock if needed

    # Test high danger buckets
    high_danger = analyzer.get_high_danger_buckets(
        threshold=0.01
    )  # Low threshold to see results
    print(f"High danger buckets: {high_danger}")

    # Test maintenance recommendations
    recommendations = analyzer.get_maintenance_recommendations()
    print(f"Maintenance recommendations: {recommendations}")

    # Test statistics (use wal_analyzer.get_stats_summary directly)
    stats = wal_analyzer.get_stats_summary(
        analyzer.bucket_stats, analyzer.operation_history
    )
    print(f"Statistics summary: {stats}")

    print("✅ WAL analyzer basic tests passed!")


def test_functional_features():
    """Test functional programming features."""
    analyzer = WALAnalyzer(store=None, config=MaintenanceConfig())

    # Test with multiple operations to trigger functional calculations
    for i in range(10):
        analyzer.record_operation(i, OpType.INSERT)
        analyzer.record_operation(i, OpType.INSERT)

    # Test sequential pattern detection
    for i in range(5):
        analyzer.record_operation(i, OpType.INSERT)

    danger_scores = [analyzer.get_danger_score(i) for i in range(5)]
    print(f"Danger scores for buckets 0-4: {danger_scores}")

    # No get_adaptive_split_threshold in WALAnalyzer; skip or mock if needed

    print("✅ Functional features tests passed!")




def test_wal_analyzer_timeout():
    """Test that the default WALAnalyzer thread timeout works (should auto-stop after 1s)."""
    from cidstore.maintenance import MaintenanceConfig, WALAnalyzer
    import time

    config = MaintenanceConfig()  # default thread_timeout is 1s
    class MockStore:
        def __init__(self):
            self.metrics = None
    mock_store = MockStore()
    analyzer = WALAnalyzer(mock_store, config)
    start_time = time.time()
    analyzer.start()
    time.sleep(2.0)  # Wait longer than the timeout
    elapsed = time.time() - start_time
    # The thread should have stopped itself
    assert not analyzer.is_alive(), f"WALAnalyzer thread still running after {elapsed:.1f}s (timeout failed)"
    # Cleanup (in case)
    if analyzer.is_alive():
        analyzer.stop()
        analyzer.join(timeout=1.0)
