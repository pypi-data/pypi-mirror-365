import socket
import pyautogui



def parse_line(line):
    print(line)
    parts = line.split(',')
    if len(parts) != 3:
        return None
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return None

def main():
	UDP_IP = "0.0.0.0"
	UDP_PORT = 5005
	SENSITIVITY = 0.1

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))

	screen_width, screen_height = pyautogui.size()
	x, y = screen_width // 2, screen_height // 2
	pyautogui.moveTo(x, y)

	try:
		while True:
			data, addr = sock.recvfrom(1024)
			line = data.decode(errors='ignore').strip()
			if line:
				values = parse_line(line)
				if values:
					ax, ay, az = values
					dx = int(ax * SENSITIVITY)
					dy = int(ay * SENSITIVITY)
					y -= dy
					x += dx
					x = max(0, min(screen_width - 1, x))
					y = max(0, min(screen_height - 1, y))
					pyautogui.moveTo(x, y)
				else:
					print(f"Skipped malformed line: {line}")
	except KeyboardInterrupt:
		sock.close()
		print("Exiting...")

if __name__ == "__main__":
	main()
