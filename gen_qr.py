import json
import requests
import multiprocessing

with open('remaining.txt', 'r') as f:
    emails = f.read().splitlines()

url = "https://backend.iitmparadox.org/sr/generate_qr/"


def send_post_request(email):
    try:
        payload = {"emails": [email]}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(
            payload), headers=headers, timeout=15)
        response.raise_for_status()
        print(f"Success: {email} -> {response.status_code}")
        return response.status_code
    except requests.RequestException as e:
        print(f"Failed: {email} -> {e}")
        return None


def main():
    num_workers = multiprocessing.cpu_count()

    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.map(send_post_request, emails)

    for email, result in zip(emails, results):
        if result is not None:
            print(f"Email: {email} - Status: {result}")
        else:
            print(f"Email: {email} - Request failed")


if __name__ == "__main__":
    main()
