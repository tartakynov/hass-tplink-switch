#! /usr/bin/env python3

# This script is used to debug the network switch client implementation
# To run this locally, you need to have virtual environment with the dependencies installed.
# You can create a virtual environment with the following command:
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
#
# Then you can run the script with the following command:
# python3 debug.py
#
# This will print the response from the network switch.

import logging
from getpass import getpass
from tlstats import TLStats

def status_to_text(status):
    statuses = {
        0: "LINKDOWN",
        2: "10MH",
        3: "10MF",
        4: "100MH",
        5: "100MF",
        6: "1000MF"
    }
    return statuses.get(status, "UNKNOWN")

# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)

    switch_host = input("network switch IP: ")
    switch_username = input("username: ")
    switch_password = getpass("password: ")

    # Create client instance
    client = TLStats(switch_host, switch_username, switch_password)

    try:
        # Get port link statuses
        statuses = client.get_port_statuses()

        if statuses is not None:
            print(f"Successfully retrieved port statuses: {statuses}")
            print(f"Total ports: {len(statuses)}")

            # Display individual port link statuses
            for i, status in enumerate(statuses):
                print(f"Port {i+1}: {status_to_text(status)}")
        else:
            print("Failed to retrieve port statuses")

    finally:
        client.close()
