import socket
import threading
import json
from datetime import datetime

ENCODER = "utf-8"
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 8000
BUFFER_SIZE = 4096


class DNSServer:
    def __init__(self, ip, port):
        self.server_ip = ip
        self.port = port
        self.records = self.load_dns_records()
        self.rr_index = {domain: 0 for domain in self.records}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.server_ip, self.port))
        print(f"[DNS SERVER] Running on {self.server_ip}:{self.port}")

    def load_dns_records(self):
        try:
            with open("dns_records.json", "r") as file:
                return json.load(file)
        except Exception as e:
            print(f"[ERROR] Could not load DNS records: {e}")
            return {}

    def log_query(self, client_ip, domain, query_type, response):
        with open("dns_queries.log", "a") as logfile:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log = f"[{timestamp}] {client_ip} requested {query_type} record for {domain} -> {response}\n"
            logfile.write(log)

    def handle_request(self, thread_id):
        print(f"[Thread-{thread_id}] Started.")
        while True:
            data, client_addr = self.socket.recvfrom(BUFFER_SIZE)
            try:
                decoded = data.decode(ENCODER)
                domain, query_type = decoded.split(",")
                domain = domain.strip()
                query_type = query_type.strip().upper()

                print(
                    f"[Thread-{thread_id}] Received query: {domain} ({query_type}) from {client_addr}"
                )

                if domain in self.records:
                    ips = self.records[domain].get(query_type, [])
                    if not ips:
                        response = f"No {query_type} record found for {domain}"
                    else:
                        index = self.rr_index[domain] % len(ips)
                        response = ips[index]
                        self.rr_index[domain] = (index + 1) % len(ips)
                else:
                    response = f"No such domain: {domain}"

                self.log_query(client_addr[0], domain, query_type, response)
                self.socket.sendto(response.encode(ENCODER), client_addr)

            except Exception as e:
                error_msg = f"Invalid request format. Error: {e}"
                print(f"[Thread-{thread_id}] {error_msg}")
                self.socket.sendto(error_msg.encode(ENCODER), client_addr)


def main():
    dns_server = DNSServer(HOST_IP, HOST_PORT)

    for i in range(3):  # Using 3 threads for concurrency
        thread = threading.Thread(
            target=dns_server.handle_request, args=(i + 1,), daemon=True
        )
        thread.start()

    threading.Event().wait()  # Keep main thread alive


if __name__ == "__main__":
    main()
