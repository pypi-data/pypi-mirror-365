"""Performance benchmarking for clause mate extraction."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class BenchmarkResult:
    """Store benchmark results."""

    execution_time: float
    memory_peak_mb: float
    memory_final_mb: float
    cpu_percent: float
    output_rows: int
    input_size_mb: float
    throughput_rows_per_sec: float


class PerformanceBenchmark:
    """Benchmark processing performance."""

    def __init__(self):
        """Initialize the performance benchmark with psutil process monitoring."""
        if psutil is None:
            raise ImportError(
                "psutil is required for benchmarking. Install with: pip install psutil"
            )
        self.process = psutil.Process()

    def benchmark_function(
        self, func: Callable, input_file: Path, output_file: Path, *args, **kwargs
    ) -> BenchmarkResult:
        """Benchmark a processing function."""
        # Initial measurements
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        input_size = input_file.stat().st_size / 1024 / 1024  # MB

        # Monitor memory during execution
        peak_memory = start_memory

        def memory_monitor():
            nonlocal peak_memory
            current = self.process.memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, current)

        # Execute function
        func(*args, **kwargs)

        # Final measurements
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = self.process.cpu_percent()

        # Output analysis
        output_rows = 0
        if output_file.exists():
            df = pd.read_csv(output_file)
            output_rows = len(df)

        execution_time = end_time - start_time
        throughput = output_rows / execution_time if execution_time > 0 else 0

        return BenchmarkResult(
            execution_time=execution_time,
            memory_peak_mb=peak_memory,
            memory_final_mb=end_memory,
            cpu_percent=cpu_percent,
            output_rows=output_rows,
            input_size_mb=input_size,
            throughput_rows_per_sec=throughput,
        )

    def compare_phases(self) -> dict[str, BenchmarkResult]:
        """Compare performance of both phases."""
        results = {}

        # Benchmark Phase 1
        from archive.phase1.clause_mates_complete import main as phase1_main

        phase1_input = Path("data/input/gotofiles/2.tsv")
        phase1_output = Path("data/output/clause_mates_phase1_export.csv")

        if phase1_input.exists():
            results["phase1"] = self.benchmark_function(
                phase1_main, phase1_input, phase1_output
            )

        # Benchmark Phase 2
        from src.main import main as phase2_main

        phase2_input = Path("data/input/gotofiles/2.tsv")
        phase2_output = Path("data/output/clause_mates_phase2_export.csv")

        if phase2_input.exists():
            results["phase2"] = self.benchmark_function(
                phase2_main, phase2_input, phase2_output
            )

        return results

    def save_benchmark_results(
        self, results: dict[str, BenchmarkResult], output_file: Path
    ):
        """Save benchmark results to file."""
        benchmark_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count() if psutil else "unknown",
                "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024
                if psutil
                else "unknown",
                "platform": platform.platform(),
            },
            "results": {},
        }

        for phase, result in results.items():
            benchmark_data["results"][phase] = {
                "execution_time": result.execution_time,
                "memory_peak_mb": result.memory_peak_mb,
                "memory_final_mb": result.memory_final_mb,
                "cpu_percent": result.cpu_percent,
                "output_rows": result.output_rows,
                "input_size_mb": result.input_size_mb,
                "throughput_rows_per_sec": result.throughput_rows_per_sec,
            }

        import json

        with open(output_file, "w") as f:
            json.dump(benchmark_data, f, indent=2)


def run_benchmarks():
    """Run performance benchmarks."""
    benchmark = PerformanceBenchmark()
    results = benchmark.compare_phases()

    output_file = Path("data/output/performance_benchmark.json")
    benchmark.save_benchmark_results(results, output_file)

    print("Performance Benchmark Results:")
    print("=" * 50)

    for phase, result in results.items():
        print(f"{phase.upper()}:")
        print(f"  Execution time: {result.execution_time:.2f}s")
        print(f"  Peak memory: {result.memory_peak_mb:.2f}MB")
        print(f"  Output rows: {result.output_rows}")
        print(f"  Throughput: {result.throughput_rows_per_sec:.2f} rows/sec")
        print()


if __name__ == "__main__":
    import platform

    run_benchmarks()
