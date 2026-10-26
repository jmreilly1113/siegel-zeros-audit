sudo -u checker -H landrun --best-effort --ro / --rw /dev -ldd -add-exec -- /usr/bin/python3 -I -c '
import socket
try: s=socket.create_connection(("1.1.1.1",443),timeout=5); print("landrun only: TCP connect 1.1.1.1:443 ALLOWED"); s.close()
except Exception as e: print("landrun only: TCP connect blocked:", e)
try: print("landrun only: DNS", socket.getaddrinfo("github.com",443)[0][4])
except Exception as e: print("landrun only: DNS blocked:", e)' 2>&1 | grep -v '^\[landrun' | head -5
