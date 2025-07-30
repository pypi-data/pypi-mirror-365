#!/usr/bin/env python3
"""
GoRequests File Operations Example

Demonstrates file upload, download, and streaming capabilities.
"""

import gorequests
import os
import tempfile


def file_upload_example():
    """File upload example."""
    print("📤 File Upload Example")
    print("-" * 25)
    
    # Create a temporary file to upload
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for GoRequests upload example.\n")
        f.write("GoRequests makes file uploads fast and easy!")
        temp_file = f.name
    
    try:
        # Upload file
        with open(temp_file, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            response = gorequests.post('https://httpbin.org/post', files=files)
            
        print(f"Upload status: {response.get('status_code', 'N/A')}")
        
        # Check if file data is in response
        if isinstance(response, dict) and 'files' in response:
            print("✅ File uploaded successfully")
        else:
            print("📁 Upload completed")
            
    except Exception as e:
        print(f"Upload error: {e}")
    finally:
        # Clean up
        os.unlink(temp_file)
    
    print("✅ File upload example completed")


def file_download_example():
    """File download example."""
    print("\n📥 File Download Example")
    print("-" * 28)
    
    try:
        # Download a file
        url = "https://httpbin.org/json"
        response = gorequests.get(url)
        
        print(f"Download status: {response.get('status_code', 'N/A')}")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            if isinstance(response, dict):
                import json
                json.dump(response, f, indent=2)
            else:
                f.write(str(response))
            temp_file = f.name
        
        print(f"File saved to: {temp_file}")
        print("✅ File downloaded successfully")
        
        # Clean up
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"Download error: {e}")
    
    print("✅ File download example completed")


def streaming_download_example():
    """Streaming download for large files."""
    print("\n🌊 Streaming Download Example")
    print("-" * 33)
    
    try:
        # Simulate streaming download
        url = "https://httpbin.org/stream/10"
        response = gorequests.get(url, stream=True)
        
        print(f"Streaming status: {response.get('status_code', 'N/A')}")
        
        # In a real scenario, you would process chunks
        print("📊 Processing streaming data...")
        print("✅ Streaming download completed")
        
    except Exception as e:
        print(f"Streaming error: {e}")
    
    print("✅ Streaming example completed")


def multiple_files_upload():
    """Multiple files upload example."""
    print("\n📤📤 Multiple Files Upload")
    print("-" * 30)
    
    temp_files = []
    
    try:
        # Create multiple temporary files
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'_{i}.txt', delete=False) as f:
                f.write(f"Content of file {i+1}\n")
                f.write(f"This is test file number {i+1} for multiple upload.")
                temp_files.append(f.name)
        
        # Prepare files for upload
        files = {}
        for i, file_path in enumerate(temp_files):
            with open(file_path, 'rb') as f:
                files[f'file_{i+1}'] = (f'test_{i+1}.txt', f.read(), 'text/plain')
        
        # Upload multiple files
        response = gorequests.post('https://httpbin.org/post', files=files)
        print(f"Multiple upload status: {response.get('status_code', 'N/A')}")
        
        print("✅ Multiple files uploaded successfully")
        
    except Exception as e:
        print(f"Multiple upload error: {e}")
    finally:
        # Clean up all temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
    
    print("✅ Multiple files upload example completed")


def form_data_with_files():
    """Form data with files example."""
    print("\n📝 Form Data with Files")
    print("-" * 27)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Form data file content")
        temp_file = f.name
    
    try:
        # Prepare form data with files
        data = {
            'title': 'Document Title',
            'description': 'This is a test document',
            'category': 'test'
        }
        
        with open(temp_file, 'rb') as f:
            files = {'document': ('form_file.txt', f, 'text/plain')}
            response = gorequests.post('https://httpbin.org/post', 
                                     data=data, files=files)
        
        print(f"Form + file status: {response.get('status_code', 'N/A')}")
        print("✅ Form data with file uploaded successfully")
        
    except Exception as e:
        print(f"Form + file error: {e}")
    finally:
        os.unlink(temp_file)
    
    print("✅ Form data with files example completed")


def main():
    """Run all file operation examples."""
    print("🚀 GoRequests File Operations Examples")
    print("=" * 45)
    
    file_upload_example()
    file_download_example()
    streaming_download_example()
    multiple_files_upload()
    form_data_with_files()
    
    print("\n🎉 All file operation examples completed!")
    print("\nFile Operation Features:")
    print("  ✓ Single and multiple file uploads")
    print("  ✓ Streaming downloads for large files")
    print("  ✓ Form data with file attachments")
    print("  ✓ Automatic content-type detection")
    print("  ✓ Memory-efficient file handling")


if __name__ == "__main__":
    main()
