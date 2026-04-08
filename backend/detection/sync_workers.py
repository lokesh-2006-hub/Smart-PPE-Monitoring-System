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
        response = requests.get(f"{api_url}/api/workers/sync", timeout=10)
        response.raise_for_status()
        workers = response.data if hasattr(response, 'data') else response.json()
        
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
