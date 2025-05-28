import socket
import json

class NetworkServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.conn = None
        self.addr = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind((host, port))
            self.sock.listen(1)
            print(f"Servidor ouvindo em {host}:{port}...")
        except socket.error as e:
            print(f"Erro ao iniciar servidor: {e}")
            raise

    def accept(self):
        try:
            self.conn, self.addr = self.sock.accept()
            print(f"Conectado com {self.addr}")
            return True
        except socket.error as e:
            print(f"Erro ao aceitar conexão: {e}")
            return False

    def send(self, data):
        try:
            if self.conn:
                msg = json.dumps(data).encode()
                self.conn.sendall(len(msg).to_bytes(4, 'big') + msg)
                return True
        except (socket.error, TypeError) as e:
            print(f"Erro ao enviar dados: {e}")
            return False

    def receive(self, timeout=None):
        if self.conn:
            if timeout is not None:
                self.conn.settimeout(timeout)
            try:
                # ler tamanho da mensagem primeiro
                raw_len = self._recvall(4)
                if not raw_len:
                    return None
                msg_len = int.from_bytes(raw_len, 'big')
                data = self._recvall(msg_len)
                if not data:
                    return None
                return json.loads(data.decode())
            except socket.timeout:
                return None
            except Exception as e:
                print(f"Erro ao receber dados: {e}")
                return None
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
        try:
            self.sock.connect((host, port))
            print(f"Conectado ao servidor {host}:{port}")
        except socket.error as e:
            print(f"Erro ao conectar: {e}")
            raise

    def send(self, data):
        msg = json.dumps(data).encode()
        self.sock.sendall(len(msg).to_bytes(4, 'big') + msg)

    def receive(self, timeout=None):
        if timeout is not None:
            self.sock.settimeout(timeout)
        try:
            raw_len = self._recvall(4)
            if not raw_len:
                return None
            msg_len = int.from_bytes(raw_len, 'big')
            data = self._recvall(msg_len)
            if not data:
                return None
            return json.loads(data.decode())
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            return None

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
