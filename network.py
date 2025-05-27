import socket
import json

class NetworkServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.conn = None
        self.addr = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(1)
        print(f"Servidor ouvindo em {host}:{port}...")

    def accept(self):
        self.conn, self.addr = self.sock.accept()
        print(f"Conectado com {self.addr}")

    def send(self, data):
        if self.conn:
            msg = json.dumps(data).encode()
            # envia tamanho da mensagem + mensagem (para evitar parcial)
            self.conn.sendall(len(msg).to_bytes(4, 'big') + msg)

    def receive(self):
        if self.conn:
            # ler tamanho da mensagem primeiro
            raw_len = self._recvall(4)
            if not raw_len:
                return None
            msg_len = int.from_bytes(raw_len, 'big')
            data = self._recvall(msg_len)
            if not data:
                return None
            return json.loads(data.decode())
        return None

    def _recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def close(self):
        if self.conn:
            self.conn.close()
        self.sock.close()

class NetworkClient:
    def __init__(self, host='localhost', port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f"Conectado ao servidor {host}:{port}")

    def send(self, data):
        msg = json.dumps(data).encode()
        self.sock.sendall(len(msg).to_bytes(4, 'big') + msg)

    def receive(self):
        raw_len = self._recvall(4)
        if not raw_len:
            return None
        msg_len = int.from_bytes(raw_len, 'big')
        data = self._recvall(msg_len)
        if not data:
            return None
        return json.loads(data.decode())

    def _recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def close(self):
        self.sock.close()
