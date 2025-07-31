import os
import json
import shelve
import glob
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class CacheManager(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

class SimpleJsonCache(CacheManager):
    def __init__(self, cache_dir, prefix, md5_checksum, expire_cache_days=30):
        # Check and remove old cache files with same prefix but different checksum
        for file in os.listdir(cache_dir):
            if file.startswith(f"{prefix}_") and file.endswith(".json"):
                old_cache_file = os.path.join(cache_dir, file)
                if f"{prefix}_{md5_checksum}.json" != file:
                    try:
                        os.remove(old_cache_file)
                    except OSError:
                        pass  # Ignore errors if file cannot be deleted

        self.cache_file = os.path.join(cache_dir, f"{prefix}_{md5_checksum}.json")
        
        # Check if cache file is older than expire_cache_days
        if os.path.exists(self.cache_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
            if datetime.now() - file_time > timedelta(days=expire_cache_days):
                try:
                    os.remove(self.cache_file)
                except OSError:
                    pass

    def get(self, key):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(key)
            except Exception:
                return None
        return None

    def set(self, key, value):
        try:
            data = {}
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data[key] = value
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return True
        except Exception:
            return False

class ShelveCache(CacheManager):
    def __init__(self, cache_dir, prefix, md5_checksum, expire_cache_days=30):
        # Check and remove old cache files with same prefix but different checksum
        for file in os.listdir(cache_dir):
            base_file = file.split('.')[0]  # Remove any extension
            if base_file.startswith(f"{prefix}_") and base_file != f"{prefix}_{md5_checksum}":
                try:
                    # Remove all shelve related files (.db, .dat, .bak, .dir)
                    file_pattern = os.path.join(cache_dir, base_file + ".*")
                    for f in glob.glob(file_pattern):
                        os.remove(f)
                except OSError:
                    pass

        self.cache_file = os.path.join(cache_dir, f"{prefix}_{md5_checksum}")

        # Check if any shelve file is older than expire_cache_days
        shelve_files = glob.glob(self.cache_file + ".*")
        if shelve_files:
            # Check the modification time of any of the shelve files
            file_time = datetime.fromtimestamp(os.path.getmtime(shelve_files[0]))
            if datetime.now() - file_time > timedelta(days=expire_cache_days):
                try:
                    # Remove all shelve related files if expired
                    for f in shelve_files:
                        os.remove(f)
                except OSError:
                    pass

    def get(self, key):
        try:
            with shelve.open(self.cache_file) as cache:
                return cache.get(key)
        except Exception as e:
            return None

    def set(self, key, value):
        try:
            with shelve.open(self.cache_file, writeback=True) as cache:
                cache[key] = value
                cache.sync()  # Force write to disk
            return True
        except Exception as e:
            return False