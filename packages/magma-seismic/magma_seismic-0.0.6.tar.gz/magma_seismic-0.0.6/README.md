# magma-seismic
Some tools for MAGMA to handle seismic

## 1. Install
```python
pip install magma-seismic
```
## 2. Import module
```python
from magma_seismic.download import Download
import magma_seismic
```
## 3. Check version
```python
magma_seismic.__version__
```
## 4. Download from Winston
```python
download = Download(
    station='LEKR',
    channel='EHZ',
    start_date='2025-05-26',
    end_date='2025-05-26',
    
    # (str, optional)
    # Change the output directory. 
    # Default to current directory
    output_directory=r'D:\Projects\magma-seismic', 
    
    # (bool, optional) 
    # Change to False to skip download 
    # when file already exists. 
    # Default False
    overwrite=True,
    
    # (bool, optional)
    # To show detailed process. 
    # Default to False
    verbose=True,
)
```

### 4.1 (Optional) Change Winston client
```python
download.set_client(
    host='winston address',
    port=123456, # winston port
    timeout=30
)
```
### 4.2 Download to IDDS
```python
download.to_idds(
    # (int, optional) 
    # Download per how many minutes. 
    # Default to 60 minutes
    period=60,
    
    # (bool, optional)
    # Merging or filling empty data/gaps. 
    # Default to False
    use_merge=True, 
)
```
### 4.3 Download to SDS
```python
download.to_sds( 
    # (bool, optional)
    # Merging or filling empty data/gaps. 
    # Default to False
    use_merge=True, 
    
    # (int, optional)
    # Use it if you unstable connection
    # It takes longer to download, but
    # can continue if the download failed.
    #
    # Download per one hour, then merged it as daily
    # Value in minutes
    chunk_size=60
)
```

## Check download result
```python
# will show list of failed download
download.failed

# will show list of successfully download
download.success 
```