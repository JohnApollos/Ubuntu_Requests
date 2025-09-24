import requests
import os
from urllib.parse import urlparse
from hashlib import sha256

# Global set to store hashes of downloaded files to prevent duplicates
downloaded_hashes = set()

def get_filename(url):
    """
    Extracts a filename from a URL, or generates a default one.
    Also sanitizes the filename to prevent security issues.
    """
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    # Basic sanitization
    filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    
    if not filename:
        filename = "downloaded_image.jpg"
        
    return filename

def fetch_and_save(url):
    """
    Fetches and saves a single image from a given URL, with precautions.
    """
    # Precaution: Check if URL is valid
    if not url.startswith(('http://', 'https://')):
        print(f"✗ Skipping {url}: Invalid URL format.")
        return

    try:
        # Precaution: Use a timeout to avoid hanging
        response = requests.get(url, timeout=10)
        
        # Check for HTTP errors
        response.raise_for_status()

        # Precaution: Check content type to ensure it's an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"✗ Skipping {url}: Content is not an image ({content_type}).")
            return

        # Precaution: Check content length to avoid large files
        content_length = int(response.headers.get('Content-Length', 0))
        if content_length > 10 * 1024 * 1024:  # 10 MB limit
            print(f"✗ Skipping {url}: File is too large ({content_length} bytes).")
            return

        # Precaution: Prevent downloading duplicate images
        image_hash = sha256(response.content).hexdigest()
        if image_hash in downloaded_hashes:
            print(f"✓ Skipping {url}: This image is a duplicate.")
            return
        
        # Add the new hash to the set
        downloaded_hashes.add(image_hash)
            
        # Get filename and save
        filename = get_filename(url)
        filepath = os.path.join("Fetched_Images", filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
            
        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {filepath}")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error for {url}: {e}")
    except Exception as e:
        print(f"✗ An unexpected error occurred for {url}: {e}")

def main():
    """Main function to run the image fetcher program."""
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    
    # Create directory if it doesn't exist
    os.makedirs("Fetched_Images", exist_ok=True)
    
    # Get URLs from user
    urls_input = input("Please enter one or more image URLs, separated by a comma: ")
    urls = [url.strip() for url in urls_input.split(',')]

    print("-" * 30)

    # Process each URL
    for url in urls:
        fetch_and_save(url)
        print("-" * 30)
    
    print("\nConnection strengthened. Community enriched.")

if __name__ == "__main__":
    main()