# Write a simple example of how to use the parallelize decorator and run it in parallel.
import logging
import time
from ray_simplify.core import parallel, parallelize, parallel_map
import timeit


@parallelize()
def square(id):
    """Calculate the square of a number."""
    # Add a small delay to simulate a time-consuming operation
    time.sleep(2)
    return id * id


def calculate_square_in_sequence(numbers):
    """Calculate squares of numbers sequentially."""
    # Use regular map to execute the square function sequentially
    results = map(square, numbers)

    return list(results)


def calculate_square_in_parallel(numbers):
    """Calculate squares of numbers in parallel."""
    # Create a parallel context
    with parallel():
        # Use parallel_map to execute the square function in parallel
        results = parallel_map(square, numbers)
        # Convert results to list while still in parallel context
        return list(results)


if __name__ == "__main__":
    # Create a list of numbers to calculate squares for
    numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    print("Running calculate_square() in sequential mode...")
    start_time = timeit.default_timer()
    results = calculate_square_in_sequence(numbers)
    duration = timeit.default_timer() - start_time
    print(f"calculate_square() executed in {duration:.4f} seconds")
    print("Results from sequential execution:")
    print(results)

    print("\nRunning calculate_square_in_parallel() in parallel mode...")
    start_time = timeit.default_timer()
    results = calculate_square_in_parallel(numbers)
    duration_parallel = timeit.default_timer() - start_time
    print(
        f"calculate_square_in_parallel() executed in {duration_parallel:.4f} seconds (including parallel context setup)"
    )
    print("Results from parallel execution:")
    print(results)
