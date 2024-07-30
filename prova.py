import threading
from datetime import datetime

ids = {}
lock = threading.Lock()

start_date = datetime(2015, 1, 1)
current_date = datetime.now()
diff = current_date - start_date

elapsed = diff.total_seconds() * 1000
print(elapsed)
print(int(elapsed))


elapsed_bin = format(elapsed, "042b")
print(f"{elapsed}")
print(f"{elapsed_bin}")

key = elapsed_bin

elapsed_bin = "000100011001100001111111101011010111010100"


for i in range(3):
	with lock:
		if key in ids:
			ids[key] = format(int(ids[key], 2)+1, "012b")
		else:
			ids[key] = format(0, "012b")
		print(ids)
