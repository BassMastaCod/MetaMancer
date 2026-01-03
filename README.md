![Logo](logo.jpg)

MetaMancer is a Python library for reading, writing, and manipulating metadata in files, specifically photos and videos.

## Features

- **Unified Metadata Interface**: Access EXIF, IPTC, and XMP metadata through a single, consistent API
- **Intelligent Caching**: Improve performance with built-in TTL caching of metadata
- **GPS Handling**: Extract coordinates, generate map URLs, and work with location data
- **Spatial Analysis**: Cluster images by location and generate interactive maps
- **Date Extraction**: Intelligently determine the most accurate creation date from various metadata information
- **Camera Information**: Extract and manipulate camera and photographer details
- **Keyword Management**: Add, remove, and manage keywords and tags

## Installation

```bash
pip install MetaMancer
```

## Usage

### Basic Metadata Access

```python
from metamancer import MetaMancer

# Get metadata for an image file
metadata = MetaMancer.get_metadata('path/to/image.jpg')  # Provide str or Path

# Access specific metadata fields
date = metadata.date
camera = metadata.camera
title = metadata.title
keywords = metadata.keywords

# Check if a specific field exists
if 'Exif.DateTimeOriginal' in metadata:
    print(f'Original date: {metadata['Exif.DateTimeOriginal']}')

# Modify metadata
metadata.title = 'My Vacation Photo'
metadata.add_keyword('vacation', 'beach', 'summer')
```

### Caching for Performance

```python
from pathlib import Path
from metamancer import MetaMancer

file_path = Path('large_image.jpg')

# First access will parse the file
metadata = MetaMancer.get_metadata(file_path)

# Subsequent accesses will use the cached data (much faster)
metadata = MetaMancer.get_metadata(file_path)

# Check if a file's metadata is cached
is_cached = MetaMancer.is_cached(file_path)

# Clear cache for a specific file
MetaMancer.clear(file_path)

# Clear entire cache
MetaMancer.clear()
```

### Location and Mapping

```python
from pathlib import Path
from metamancer import MetaMancer
import glob

# Get all jpg files in a directory
image_files = [Path(f) for f in glob.glob('vacation_photos/*.jpg')]

# Generate an interactive map with all geotagged photos
MetaMancer.generate_photo_map(image_files, 'vacation_map.html')

# Get coordinates for a specific image
metadata = MetaMancer.get_metadata(image_files[0])
if metadata.has_location():
    lat, lon = metadata.get_gps_coords()
    map_url = metadata.get_gps_url()  # Google Maps URL
    print(f'Photo taken at: {lat}, {lon}')
    print(f'View on map: {map_url}')
```

#### Spatial Clustering

```python
# Cluster images by location
spatial_strata = MetaMancer.cluster(image_files)

# Access files in the root level
print(f'Total files: {len(spatial_strata.files)}')

# Access files in a specific location cluster
if 'Beach' in spatial_strata._nested_files:
    beach_photos = spatial_strata['Beach'].files
    print(f'Beach photos: {len(beach_photos)}')
```

## TODO

This library is currently in its Alpha release.
It is in active development, but there is still a lot of work to do, including:
- [ ] Fully documented functions
- [ ] More detailed examples, emphasizing various classes
- [ ] Many more fields supported (only started with the bare minimum)
- [ ] Setting/modifying metadata values
- [ ] Check in test code (once it doesn't involve personal photos)
- [ ] Video file support
- [ ] Configuration, specifically around caching
- [ ] More thoughtful README
- [ ] More world-building!
- [ ] Links to projects that use MetaMancer
