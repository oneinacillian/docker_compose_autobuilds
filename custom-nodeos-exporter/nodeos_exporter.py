from prometheus_client import start_http_server, Gauge
import requests
import time
from datetime import datetime

# Define Prometheus metrics
head_block_number = Gauge("nodeos_head_block_number", "Head block number")
head_block_time = Gauge("nodeos_head_block_time", "Head block time as Unix timestamp")
head_block_producer = Gauge("nodeos_head_block_producer", "Head block producer", ["producer"])
last_irreversible_block_number = Gauge("nodeos_last_irreversible_block_number", "Last irreversible block number")
last_irreversible_block_time = Gauge("nodeos_last_irreversible_block_time", "Last irreversible block time as Unix timestamp")
producer_rounds = Gauge("nodeos_producer_rounds", "Number of rounds completed by each producer", ["producer"])

def fetch_nodeos_data(url):
    """
    Fetch data from the Nodeos API.
    Returns the JSON response if successful, or None if an error occurs.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Nodeos API: {e}")
        return None

def process_metrics(data, current_producer, producer_round_counts):
    """
    Process and update Prometheus metrics based on Nodeos data.
    """
    try:
        # Update head block number
        head_block_number.set(data["head_block_num"])

        # Convert head block time to Unix timestamp and update metric
        head_block_time_iso = data["head_block_time"]
        head_block_time_unix = datetime.fromisoformat(head_block_time_iso.replace("Z", "+00:00")).timestamp()
        head_block_time.set(head_block_time_unix)

        # Update producer
        producer = data["head_block_producer"]

        # Count rounds only when the producer changes
        if current_producer != producer:
            if producer not in producer_round_counts:
                producer_round_counts[producer] = 0
            producer_round_counts[producer] += 1
            producer_rounds.labels(producer=producer).set(producer_round_counts[producer])

        # Update the Prometheus producer metric
        if current_producer and current_producer != producer:
            head_block_producer.clear()  # Removes all existing labels
        head_block_producer.labels(producer=producer).set(1)

        # Update last irreversible block number
        last_irreversible_block_number.set(data["last_irreversible_block_num"])

        # Convert last irreversible block time to Unix timestamp and update metric
        last_irreversible_block_time_iso = data["last_irreversible_block_time"]
        last_irreversible_block_time_unix = datetime.fromisoformat(last_irreversible_block_time_iso.replace("Z", "+00:00")).timestamp()
        last_irreversible_block_time.set(last_irreversible_block_time_unix)

        return producer
    except KeyError as e:
        print(f"Missing key in Nodeos data: {e}")
    except ValueError as e:
        print(f"Error processing block time: {e}")
    except Exception as e:
        print(f"Unexpected error processing metrics: {e}")
    return current_producer  # Return the current producer unchanged in case of error

def collect_metrics():
    """
    Main loop to collect metrics and update Prometheus.
    """
    nodeos_url = "http://node:8888/v1/chain/get_info"
    current_producer = None  # Track the current producer to manage label updates
    producer_round_counts = {}  # Track the number of rounds for each producer

    while True:
        data = fetch_nodeos_data(nodeos_url)
        if data:
            current_producer = process_metrics(data, current_producer, producer_round_counts)
        else:
            print("Skipping metric update due to failed data fetch.")
        time.sleep(1)

if __name__ == "__main__":
    # Start Prometheus metrics server
    try:
        start_http_server(8000)
        print("Prometheus metrics server started on port 8000")
        collect_metrics()
    except Exception as e:
        print(f"Fatal error starting the metrics server: {e}")
