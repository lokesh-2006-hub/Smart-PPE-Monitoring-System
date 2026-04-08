import requests
import os
import base64
import argparse

def sync_workers(api_url, output_dir):
    print(f"Syncing workers from {api_url} to {output_dir}...")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    try:
        # Retry logic for Render spin-up
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Connection attempt {attempt + 1}/{max_retries}...")
                response = requests.get(f"{api_url}/api/workers/sync", timeout=60)
                response.raise_for_status()
                break
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if attempt == max_retries - 1:
                    raise
                print("Server is waking up... waiting 10 seconds before retry.")
                import time
                time.sleep(10)
        
        workers = response.json()
        
        print(f"Found {len(workers)} workers with photos.")
        
        for worker in workers:
            name = worker.get('name', 'Unknown').replace(" ", "_")
            photo_data = worker.get('photo_url')
            
            if not photo_data:
                continue
                
            # Create worker specific directory
            worker_dir = os.path.join(output_dir, name)
            if not os.path.exists(worker_dir):
                os.makedirs(worker_dir)
            
            # Extract base64 part
            try:
                if "," in photo_data:
                    header, encoded = photo_data.split(",", 1)
                else:
                    encoded = photo_data
                
                image_data = base64.b64decode(encoded)
                photo_path = os.path.join(worker_dir, f"{name}.jpg")
                
                with open(photo_path, "wb") as f:
                    f.write(image_data)
                
                print(f"  ✓ Synced: {name}")
            except Exception as e:
                print(f"  ✗ Failed to sync {name}: {e}")
                
        print("Sync complete.")
        return True
    except Exception as e:
        print(f"Error during sync: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="https://smart-ppe-monitoring-system1.onrender.com")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    
    # Default output dir relative to script
    if not args.output_dir:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Look for backend/data/known_faces
        backend_root = os.path.dirname(script_dir)
        args.output_dir = os.path.join(backend_root, "data", "known_faces")
        
    sync_workers(args.api_url, args.output_dir)
