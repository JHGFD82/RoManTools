# decorators.py
import time
import sys

# Initialize the counter for the number of tests
test_counter = 0

def timeit_decorator(repeats=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            global test_counter
            test_counter += 1
            total_time = 0.0
            result = 0
            for i in range(repeats):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs, repeat_num=i + 1)
                except TypeError:
                    result = func(*args, **kwargs)  # Fallback for functions that don't accept repeat_num
                end_time = time.time()
                total_time += end_time - start_time
            average_time = total_time / repeats
            original_stdout = sys.__stdout__
            print(f"Test {test_counter}: Function {func.__name__} executed in average: {average_time:.8f} seconds over {repeats} runs", file=original_stdout)
            return result
        return wrapper
    return decorator
