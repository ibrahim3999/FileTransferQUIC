import socket
import random
import time

from api import unpack_long_header, pack_short_header, unpack_short_header, generate_random_file, print_statistics

connections = {}


def start_quic_server():
    server_address = ('localhost', 4433)
    buffer_size = 4096

    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(server_address)
        print("QUIC server is running...")

        while True:
            data, client_address = server_socket.recvfrom(buffer_size)
            print(f"Received {len(data)} bytes from {client_address}")

            if client_address not in connections:
                connection_id, packet_number, payload = unpack_long_header(data)
                print(f"Initial connection ID: {connection_id}, Packet number: {packet_number}, Payload: {payload}")
                connections[client_address] = {
                    'connection_id': connection_id,
                    'flows': [],
                    'last_packet_number': packet_number
                }
                response = pack_short_header(packet_number, payload)
                server_socket.sendto(response, client_address)
                print(f"Sent {len(response)} bytes back to {client_address}")

                # Initialize flows
                num_flows = 5
                for i in range(num_flows):
                    packet_size = random.randint(1000, 2000)
                    flow = {
                        'id': i,
                        'packet_size': packet_size,
                        'total_bytes': 0,
                        'total_packets': 0,
                        'start_time': 0,
                        'end_time': 0
                    }
                    connections[client_address]['flows'].append(flow)

            else:
                packet_number, payload = unpack_short_header(data)
                print(f"Packet number: {packet_number}, Payload: {payload}")

                # Update statistics
                for flow in connections[client_address]['flows']:
                    flow['total_bytes'] += len(payload)
                    flow['total_packets'] += 1
                    if flow['start_time'] == 0:
                        flow['start_time'] = time.time()
                    flow['end_time'] = time.time()

                response = pack_short_header(packet_number, payload)
                server_socket.sendto(response, client_address)
                print(f"Sent {len(response)} bytes back to {client_address}")


if __name__ == '__main__':
    start_quic_server()
