import socket
import threading
import json
import sqlite3
import queue
import base64
import signal

class PoopyLog:
    @staticmethod
    def log(message):
        print(f"\033[38;5;94m[Sqlpoop]\033[92m {message}\033[0m")

def encode_bytes(obj):
    if isinstance(obj, bytes):
        return {"__bytes__": True, "base64": base64.b64encode(obj).decode("utf-8")}
    elif isinstance(obj, (list, tuple)):
        return [encode_bytes(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: encode_bytes(value) for key, value in obj.items()}
    else:
        return obj

def decode_bytes(obj):
    if isinstance(obj, dict) and obj.get("__bytes__"):
        return base64.b64decode(obj["base64"])
    elif isinstance(obj, list):
        return [decode_bytes(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: decode_bytes(value) for key, value in obj.items()}
    else:
        return obj

class Sqlpoop:
    def __init__(self, dbfile="sqlpoop.db", passcode="secret", host="127.0.0.1", port=5000):
        self.dbfile = dbfile
        self.passcode = passcode
        self.host = host
        self.port = port
        self._conn = sqlite3.connect(self.dbfile, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.commit()
        self._write_queue = queue.Queue()
        self._client_lock = threading.Lock()
        self._cursor_lock = threading.Lock()
        self.shutdown_event = threading.Event()
        self._server_socket = None
        self._worker_thread = threading.Thread(target=self._write_worker, daemon=True)
        self._worker_thread.start()
        self._server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self._server_thread.start()
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTSTP, self._signal_handler)

    def _write_worker(self):
        while not self.shutdown_event.is_set():
            try:
                client_socket, query, params = self._write_queue.get(timeout=1)
            except queue.Empty:
                continue
            try:
                with self._cursor_lock:
                    cursor = self._conn.cursor()
                    cursor.execute(query, params)
                    self._conn.commit()
                    response = {"status": "ok", "rowcount": cursor.rowcount}
            except Exception as e:
                response = {"status": "error", "error": str(e)}
                PoopyLog.log(str(e))
            try:
                client_socket.sendall((json.dumps(response) + "\n").encode())
            except Exception:
                pass
            client_socket.close()
            self._write_queue.task_done()

    def _handle_client(self, client_socket):
        try:
            data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break
            msg = data.decode().strip()
            req = json.loads(msg)
            if req.get("passcode") != self.passcode:
                client_socket.sendall(json.dumps({"status": "error", "error": "Invalid passcode"}).encode() + b"\n")
                client_socket.close()
                return
            query = req.get("query")
            params = decode_bytes(req.get("params", ()))
            if not query:
                client_socket.sendall(json.dumps({"status": "error", "error": "No query provided"}).encode() + b"\n")
                client_socket.close()
                return
            if query.strip().lower().startswith("select"):
                with self._cursor_lock:
                    cursor = self._conn.cursor()
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                rows = encode_bytes(rows)
                response = {"status": "ok", "rows": rows}
                client_socket.sendall((json.dumps(response) + "\n").encode())
                client_socket.close()
            else:
                self._write_queue.put((client_socket, query, params))
        except Exception as e:
            PoopyLog.log(str(e))
            try:
                client_socket.sendall(json.dumps({"status": "error", "error": str(e)}).encode() + b"\n")
            except Exception:
                pass
            client_socket.close()

    def _server_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self._server_socket = s
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            PoopyLog.log(f"Poopy server made at {self.host}:{self.port}")
            s.settimeout(1.0)
            while not self.shutdown_event.is_set():
                try:
                    client_socket, addr = s.accept()
                except socket.timeout:
                    continue
                threading.Thread(target=self._handle_client, args=(client_socket,), daemon=True).start()

    def _send_request(self, query, params=()):
        req = {"passcode": self.passcode, "query": query, "params": encode_bytes(params)}
        with self._client_lock:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                sock.sendall((json.dumps(req) + "\n").encode())
                data = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if b"\n" in data:
                        break
                resp = json.loads(data.decode().strip())
                resp_rows = resp.get("rows")
                if resp_rows is not None:
                    resp["rows"] = decode_bytes(resp_rows)
                return resp

    def cursor(self):
        return SqlpoopCursor(self)

    def commit(self):
        pass

    def close(self):
        self._conn.close()

    def execute(self, query, params=()):
        resp = self._send_request(query, params)
        if resp["status"] == "ok":
            return SqlpoopResult(resp)
        else:
            raise Exception(resp.get("error", "Unknown error"))

    def executemany(self, query, seq_of_params):
        results = []
        for params in seq_of_params:
            resp = self._send_request(query, params)
            if resp["status"] == "ok":
                results.append(SqlpoopResult(resp))
            else:
                raise Exception(resp.get("error", "Unknown error"))
        return results

    def _signal_handler(self, signum, frame):
        PoopyLog.log(f"Signal {signum} received, shutting down...")
        self.shutdown()
        sys.exit(0)

    def shutdown(self):
        if self.shutdown_event.is_set():
            return
        self.shutdown_event.set()
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
        self._worker_thread.join(timeout=2)
        self._server_thread.join(timeout=2)
        self._conn.close()
        PoopyLog.log("Server shut down cleanly.")


class SqlpoopCursor:
    def __init__(self, db):
        self.db = db
        self._last_result = None

    def execute(self, query, params=()):
        self._last_result = self.db.execute(query, params)
        return self

    def executemany(self, query, seq_of_params):
        self._last_result = self.db.executemany(query, seq_of_params)
        return self

    def fetchall(self):
        if self._last_result:
            return self._last_result.fetchall()
        return []

    def fetchone(self):
        if self._last_result:
            return self._last_result.fetchone()
        return None

    def fetchmany(self, size=None):
        if self._last_result:
            return self._last_result.fetchmany(size)
        return []

    def close(self):
        pass

class SqlpoopResult:
    def __init__(self, resp):
        self.resp = resp
        self._rows = resp.get("rows", [])
        self._index = 0
        self.rowcount = resp.get("rowcount", -1)

    def fetchall(self):
        return self._rows

    def fetchone(self):
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return row
        return None

    def fetchmany(self, size=1):
        if self._index >= len(self._rows):
            return []
        end = self._index + (size or 1)
        rows = self._rows[self._index:end]
        self._index = min(end, len(self._rows))
        return rows

class SqlpoopClient:
    def __init__(self, passcode="secret", host="127.0.0.1", port=5000):
        self.passcode = passcode
        self.host = host
        self.port = port
        self._client_lock = threading.Lock()

    def _send_request(self, query, params=()):
        req = {"passcode": self.passcode, "query": query, "params": encode_bytes(params)}
        with self._client_lock:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                sock.sendall((json.dumps(req) + "\n").encode())
                data = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if b"\n" in data:
                        break
                resp = json.loads(data.decode().strip())
                resp_rows = resp.get("rows")
                if resp_rows is not None:
                    resp["rows"] = decode_bytes(resp_rows)
                return resp

    def cursor(self):
        return SqlpoopCursor(self)

    def execute(self, query, params=()):
        resp = self._send_request(query, params)
        if resp["status"] == "ok":
            return SqlpoopResult(resp)
        else:
            raise Exception(resp.get("error", "Unknown error"))

    def executemany(self, query, seq_of_params):
        results = []
        for params in seq_of_params:
            resp = self._send_request(query, params)
            if resp["status"] == "ok":
                results.append(SqlpoopResult(resp))
            else:
                raise Exception(resp.get("error", "Unknown error"))
        return results

    def commit(self):
        pass

    def close(self):
        pass
