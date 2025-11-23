import time
start = time.time()
print("Importing main...")
try:
    import main
    print(f"Import success in {time.time() - start:.2f}s")
except Exception as e:
    print(f"Import failed: {e}")
