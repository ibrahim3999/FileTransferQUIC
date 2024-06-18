import socket
import random
import time
from api import generate_connection_id, generate_packet_number, pack_long_header, pack_short_header, unpack_short_header, generate_random_file, print_statistics

def start_quic_client():
    server_address = ('localhost', 4433)
    buffer_size = 4096

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        connection_id = generate_connection_id()
        packet_number = generate_packet_number()
        message = b"Hello, QUIC server!"

        # Pack the long header with the initial connection ID and packet number
        packet = pack_long_header(connection_id, packet_number, message)
        print(f"Sending initial packet with connection ID {connection_id} and packet number {packet_number}")
        client_socket.sendto(packet, server_address)

        # Receive the response with the short header
        data, server = client_socket.recvfrom(buffer_size)
        response_packet_number, payload = unpack_short_header(data)
        print(f"Received packet number {response_packet_number} with {len(payload)} bytes from {server}")

        # Initialize flows
        flows = []
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
            flows.append(flow)

        # Send data packets for each flow
        for flow in flows:
            message = generate_random_file(flow['packet_size'])
            packet_number = generate_packet_number()
            packet = pack_short_header(packet_number, message)
            print(f"Sending packet number {packet_number} with {len(message)} bytes to {server_address}")
            flow['start_time'] = time.time()
            client_socket.sendto(packet, server_address)

            # Receive and print the response
            data, server = client_socket.recvfrom(buffer_size)
            response_packet_number, payload = unpack_short_header(data)
            print(f"Received packet number {response_packet_number} with {len(payload)} bytes from {server}")
            flow['end_time'] = time.time()
            flow['total_bytes'] += len(payload)
            flow['total_packets'] += 1

        # Print statistics
        print_statistics(flows)

if __name__ == '__main__':
    start_quic_client()
