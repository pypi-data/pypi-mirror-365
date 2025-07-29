from azure.storage.blob import BlobServiceClient
import logging

class BlobClient:
    def __init__(self, connection_string: str, container_name: str, blob_name: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        
        # Create container if it doesn't exist
        if not self.container_client.exists():
            self.container_client.create_container()
            logging.info(f"Created container '{container_name}'")
            
        logging.info(f"Initialized BlobClient for container '{container_name}' and blob '{blob_name}'")

    def upload_blob(self, content):
        try:
            self.blob_client.upload_blob(content, overwrite=True)
            logging.info(f"Uploaded blob '{self.blob_client.blob_name}'")
        except Exception as e:
            logging.error(f"Upload failed: {str(e)}")
            raise

    def read_blob(self):
        try:
            blob_data = self.blob_client.download_blob()
            return blob_data.readall().decode('utf-8')
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            raise

def setup_azurite():
    connection_string = (
        "DefaultEndpointsProtocol=http;"
        "AccountName=devstoreaccount1;"
        "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
        "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    )
    container_name = "mycontainer"
    blob_name = "presets/scheduled_presets.csv"
    
    return BlobClient(connection_string, container_name, blob_name)