import os
import json
from rocketcontent.content_config import ContentConfig
import requests
import urllib3
import warnings
import logging
from copy import deepcopy
from rocketcontent.cache_manager import SimpleJsonCache, ShelveCache
from rocketcontent.util import convert_date_format, previous_day
from collections import defaultdict
import shelve 

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentClassNavigator:
    """
    ContentClassNavigator provides methods to interact with content classes in the Content Repository.
    """

    def __init__(self, content_config, expire_cache_days=30):
        """
        Initializes the ContentClassNavigator class with the given configuration.
        Args:
            content_config (ContentConfig): Configuration object with repository connection and authentication details.
        Raises:
            TypeError: If content_config is not an instance of ContentConfig.
        """
        if isinstance(content_config, ContentConfig):
            self.repo_url = content_config.repo_url
            self.repo_id = content_config.repo_id
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
            self.class_navigator_cache_page_limit = content_config.class_navigator_cache_page_limit

            # Set cache_file as an attribute using the directory from config_file and repo_id
            config_dir = os.path.dirname(content_config.config_file)
            cache_dir = os.path.join(config_dir, "_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Initialize cache managers
            self.content_cache = SimpleJsonCache(cache_dir, f"cache_cc_{self.repo_id}",
                                                 content_config.md5_checksum,
                                                 expire_cache_days=content_config.class_navigator_cache_days_cc)
            # Shelve cache for reports and versions)
            self.reports_cache = ShelveCache(cache_dir, f"cache_reports_{self.repo_id}",
                                             content_config.md5_checksum,
                                             expire_cache_days=self.class_navigator_cache_days_reports)        
            
            self.versions_cache = ShelveCache(cache_dir, f"cache_versions_{self.repo_id}",
                                              content_config.md5_checksum, 
                                              expire_cache_days=self.class_navigator_cache_days_versions)
        else:
            raise TypeError("ContentConfig class object expected")

    def _get_content_class_id(self):
        """
        Gets the objectId of the 'Content Classes' content class using simple JSON cache.
        """
        # Try from cache first
        object_id = self.content_cache.get("objectId")
        if object_id:
            self.logger.info("'Content Classes 'objectId obtained from cache.")
            return object_id
        
        headers = deepcopy(self.headers)
        headers["Accept"] = "application/vnd.asg-mobius-navigation.v1+json"

        # If not in cache, make the request
        content_class_id_url = f"{self.repo_url}/repositories/{self.repo_id}/children?limit=1"
        self.logger.info("--------------------------------")
        self.logger.info("Method : _get_content_class_id")
        self.logger.debug(f"URL : {content_class_id_url}")
        self.logger.debug(f"Headers : {json.dumps(headers)}")

        headers = deepcopy(self.headers)
        headers["Accept"] = "application/vnd.asg-mobius-navigation.v1+json"
        
        try:

            response = requests.get(content_class_id_url, headers=headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    if item.get("name") == "Content Classes":
                        object_id = item.get("objectId")
                        self.content_cache.set("objectId", object_id)
                        return object_id
                raise ValueError("'Content Classes' not found in response.")
            else:
                self.logger.debug(response.text)
                raise ValueError(f"Request error: {response.status_code}")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise


    def get_reports_id(self, report_id):
        """
        Gets the objectId of the Reports using shelve cache for multiple reports.
        """
        cc_enc_id = self._get_content_class_id()

        report_id = report_id.strip()
        
        # Try from cache first
        object_id = self.reports_cache.get(report_id)
        if object_id:
            self.logger.info(f"objectId for Reports '{report_id}' obtained from cache.")
            return object_id

        headers = deepcopy(self.headers)
        headers["Accept"] = "application/vnd.asg-mobius-navigation.v1+json"

        # If not in cache, make the request
        reports_id_url = f"{self.repo_url}/folders/{cc_enc_id}/children?locate={report_id}&limit=1"

        self.logger.info("--------------------------------")
        self.logger.info("Method : get_reports_id")
        self.logger.debug(f"URL : {reports_id_url}")
        self.logger.debug(f"Headers : {json.dumps(headers)}")
        try:
            response = requests.get(reports_id_url, headers=headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    rep = str(item.get("name") ).strip()
                    if rep == report_id:
                        object_id = item.get("objectId")
                        self.reports_cache.set(report_id, object_id)
                        return object_id
                raise ValueError("'Reports' not found in response.")
            else:
                self.logger.debug(response.text)
                raise ValueError(f"Request error: {response.status_code}")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise


    def get_versions(self, report_id, version_from, version_to):
        """
        Gets the objectIds of the Reports within a date range using pagination and shelve cache.
        
        Args:
            report_id (str): Report identifier           
            version_from (str): Start date in format 'MMM dd, yyyy HH:mm:ss aa'
            version_to (str): End date in format 'MMM dd, yyyy HH:mm:ss aa'
        
        Returns:
            dict: Dictionary with version_key:object_id pairs for versions within range
        """

        # Report object identifier
        report_object_id = content_obj.get_reports_id(report_id)  

        report_versions = defaultdict(str)
        limit = self.class_navigator_cache_page_limit

        version_locate = version_to
                 
        headers = deepcopy(self.headers)
        headers["Accept"] = "application/vnd.asg-mobius-navigation.v1+json"
        
        while True:
            # If not in cache, make the request with pagination
            reports_id_url = f"{self.repo_url}/folders/{report_object_id}/children?locate={version_locate}&limit={limit}"
            
            self.logger.info("--------------------------------")
            self.logger.info("Method : get_versions")
            self.logger.debug(f"URL : {reports_id_url}")
            
            try:
                response = requests.get(reports_id_url, headers=headers, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    # If no more items, break the loop
                    if not items:
                        break
                        
                    for item in items:
                        version = str(item.get("name")).strip()
                        version_formatted = convert_date_format(version)
                        
                        # If we've passed the end date, we can stop
                        if version_formatted > version_to:
                            return report_versions
                        
                        # Check if version is within range
                        if version_from <= version_formatted <= version_to:
                            version_key = f"{report_id}_{version_formatted}"
                            object_id = item.get("objectId")
                            
                            # Check cache first
                            cached_id = self.versions_cache.get(version_key)
                            if not cached_id:
                                # Save to cache if not present
                                self.versions_cache.set(version_key, object_id)
                                
                            report_versions[version_key] = object_id
                    
                    # Update offset for next page
                    version_locate = previous_day(version_formatted)
                    
                    # If no more items to fetch, break
                    if not data.get("hasMoreItems", False):
                        break
                        
                else:
                    self.logger.debug(response.text)
                    raise ValueError(f"Request error: {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
                raise
                
        return report_versions

    def retrieve_cache_versions(self, report_id, version_from, version_to):
        """
        Retrieves report versions from cache only, within the specified date range.
        
        Args:
            report_id (str): Report identifier
            version_from (str): Start date in format 'MMM dd, yyyy HH:mm:ss aa'
            version_to (str): End date in format 'MMM dd, yyyy HH:mm:ss aa'
        
        Returns:
            dict: Dictionary with version_key:object_id pairs for versions within range
        """
       
        report_versions = defaultdict(str)
        self.logger.info("--------------------------------")
        self.logger.info("Method : retrieve_cache_versions")        
        
        # Get all keys from versions cache that start with report_id
        with shelve.open(self.versions_cache.cache_file) as cache:
            for key in cache.keys():
                if key.startswith(f"{report_id}_"):
                    # Extract the version date from the key
                    try:
                        version_date = key.split('_')[1]
                        # Check if version is within range
                        if version_from <= version_date <= version_to:
                            report_versions[key] = cache[key]
                    except IndexError:
                        continue
        
        self.logger.info(f"Retrieved {len(report_versions)} versions from cache for report {report_id}")
        return report_versions

# Ejecutar la función de test
if __name__ == "__main__":
    # Configure logger
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('requests').setLevel(logging.CRITICAL)

    logger = logging.getLogger('')
    logger.handlers = []
    logger.setLevel(getattr(logging, "DEBUG"))
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    config_file = 'C:\\git\\content-python-library\\dev\\conf\\rocketcontent.8682.yaml'  # Ensure this file exists
    content_config_obj = ContentConfig(config_file)

    content_obj = ContentClassNavigator(content_config_obj, expire_cache_days=30)
    

    print("--------------------------------------")
    col = content_obj.retrieve_cache_versions("AC2020", "20220401000000", "20220801000000")

    if len(col) == 0:
       content_obj.get_versions("AC2020", "20220401000000", "20220801000000")
       col = content_obj.retrieve_cache_versions("AC2020", "20220401000000", "20220801000000")
    
    for key, value in col.items():  
        print(f"Version Key: {key}, Object ID: {value}") 

    print("--------------------------------------")


