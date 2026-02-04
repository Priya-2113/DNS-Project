import socket

ENCODER = "utf-8"
DEST_IP = "192.168.15.20"
DEST_PORT = 8000
BUFFER_SIZE = 4096


class DNSClient:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def query(self, domain, query_type="A"):
        message = f"{domain},{query_type}"
        self.client_socket.sendto(message.encode(ENCODER), (self.server_ip, self.port))
        response, _ = self.client_socket.recvfrom(BUFFER_SIZE)
        return response.decode(ENCODER)


def main():
    client = DNSClient(DEST_IP, DEST_PORT)
    print("[DNS CLIENT] Started")

    while True:
        domain = input("Enter domain (or 'exit' to quit): ").strip()
        if domain.lower() == "exit":
            break

        query_type = input("Enter record type (A or AAAA): ").strip().upper()
        if query_type not in ("A", "AAAA"):
            print("Invalid query type. Use A or AAAA.")
            continue

        try:
            response = client.query(domain, query_type)
            print(f"Response: {response}")
        except Exception as e:
            print(f"[ERROR] Failed to get response: {e}")


if __name__ == "__main__":
    main()
