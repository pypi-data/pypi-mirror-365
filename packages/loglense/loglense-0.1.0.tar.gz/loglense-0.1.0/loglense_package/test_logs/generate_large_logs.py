# This file helps in generating large log files for testing purposes
import sys
import random

if len(sys.argv) != 2:
    print("Usage: python generate_log.py <size_in_mb>")
    sys.exit(1)

try:
    size_mb = int(sys.argv[1])
except ValueError:
    print("Error: Please provide a valid integer for the size in MB.")
    sys.exit(1)

target_size_bytes = size_mb * 1024 * 1024
current_size = 0

info_log = "INFO: User authentication successful for user_id={}\n"
error_log = "ERROR: Failed to connect to database on host db-prod-01. Caused by: ConnectionTimeout\n"

with open("large_test.log", "w") as f:
    while current_size < target_size_bytes:
        # Write 9 info logs for every 1 error log
        for i in range(9):
            line = info_log.format(random.randint(1000, 9999))
            f.write(line)
            current_size += len(line)
        
        line = error_log
        f.write(line)
        current_size += len(line)

print(f"✅ Generated large_test.log (~{size_mb} MB)")
