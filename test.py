import requests
import concurrent.futures

url = 'http://localhost:8000/fest/fest_register/'

bearer_token = '895Euh3DyejTcnDfJ9sdz7KWFTQkgM'


data = {
    "arrival_date": "2024-02-12T09",
    "departure_date": "2024-02-12T09",
    "dob": "2024-02-12T09:27",
    "gender": "Male",
    "likelihood": "mostly",
    "country": "India",
    "city": "Gotham",
    "state": "Bihar",
    "whatsapp": "6942069420"
}

# Define headers with Authorization Bearer token
headers = {
    'Authorization': f'Bearer {bearer_token}',
    'Content-Type': 'application/json'
}

# Define the number of requests you want to send
num_requests = 100

# Function to send a single request


def send_request(url):
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Response Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Stress test the endpoint
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit multiple requests concurrently
    futures = [executor.submit(send_request, url) for _ in range(num_requests)]

    # Wait for all requests to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred: {e}")
