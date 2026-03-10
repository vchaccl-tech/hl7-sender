import socket
import datetime

def start_mock_server(host='127.0.0.1', port=2575):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Mock HL7 Server listening on {host}:{port}")

    VT = b'\x0b'
    FS = b'\x1c'
    CR = b'\x0d'

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")
        with conn:
            data = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
                if data.endswith(FS + CR):
                    break
            
            if data:
                print(f"Received raw data: {data}")
                # Unwrap
                if data.startswith(VT) and data.endswith(FS + CR):
                    msg_content = data[1:-2].decode('utf-8')
                    print(f"Received HL7 Message:\n{msg_content}")
                    
                    # Generate ACK
                    # Simple ACK: MSH|^~\&|MOCK_SERVER||SENDER||YYYYMMDDHHMMSS||ACK|MSGID|P|2.3
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    ack_msg = f"MSH|^~\\&|MOCK_SERVER||SENDER||{timestamp}||ACK|MSGID|P|2.3\rMSA|AA|MSGID"
                    
                    wrapped_ack = VT + ack_msg.encode('utf-8') + FS + CR
                    conn.sendall(wrapped_ack)
                    print("Sent ACK")
                else:
                    print("Received invalid MLLP frame")

if __name__ == "__main__":
    try:
        start_mock_server()
    except KeyboardInterrupt:
        print("\nServer stopped.")
