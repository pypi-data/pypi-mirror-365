import itkdb
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import requests
import csv
from io import StringIO
import os
from datetime import datetime, timedelta

__version__ = "1.5.0"

# Configuration - you can override these by setting environment variables
DEFAULT_API_BASE_URL = "https://key-version-tester.app.cern.ch"

############
## Authentication token for creating ITKSpecClient
############

class AuthToken:
    """Authentication token object required to create ITKSpecClient"""
    
    def __init__(self, token: str, expiry: datetime, access_code1: str, access_code2: str):
        """
        Internal constructor - should not be called directly
        Use authenticate() function to get an AuthToken
        """
        self._token = token
        self._expiry = expiry
        self._access_code1 = access_code1
        self._access_code2 = access_code2
    
    def is_valid(self) -> bool:
        """Check if the authentication token is still valid"""
        return datetime.now() < self._expiry
    
    def time_remaining(self) -> timedelta:
        """Get the remaining time before the token expires"""
        if not self.is_valid():
            return timedelta(0)
        return self._expiry - datetime.now()

def authenticate(access_code1: str, access_code2: str) -> AuthToken:
    """
    Authenticate with ITKDB and return an AuthToken required to create clients
    
    Args:
        access_code1: First access code for ITKDB authentication
        access_code2: Second access code for ITKDB authentication
    
    Returns:
        AuthToken object required to create ITKSpecClient
        
    Raises:
        Exception: If authentication fails
        
    Example:
        auth_token = itkspec.authenticate('access_code1', 'access_code2')
        client = itkspec.ITKSpecClient(auth_token)
    """
    api_base_url = DEFAULT_API_BASE_URL
    auth_url = f"{api_base_url}/auth"
    auth_data = {
        "access_code1": access_code1,
        "access_code2": access_code2
    }
    
    try:
        response = requests.post(auth_url, json=auth_data)
        response.raise_for_status()
        
        auth_response = response.json()
        token = auth_response["access_token"]
        expiry = datetime.now() + timedelta(minutes=60)  # Default expiry time of 60 minutes
        
        return AuthToken(token, expiry, access_code1, access_code2)
        
    except requests.RequestException as e:
        raise Exception(f"Authentication failed: {str(e)}")

class ITKSpecClient:
    """Main client class for ITK Specifications API"""
    
    def __init__(self, auth_token: AuthToken):
        """
        Initialize the ITK Spec client with an AuthToken
        
        Args:
            auth_token: AuthToken object obtained from authenticate() function
        
        Raises:
            Exception: If auth_token is invalid or expired
            
        Example:
            auth_token = itkspec.authenticate('access_code1', 'access_code2')
            client = itkspec.ITKSpecClient(auth_token)
        """
        if not isinstance(auth_token, AuthToken):
            raise TypeError("Client requires an AuthToken. Use authenticate() function first.")
        
        if not auth_token.is_valid():
            raise Exception("AuthToken has expired. Please authenticate again.")
        
        self.auth_token = auth_token
        self.api_base_url = DEFAULT_API_BASE_URL
    
    # checking jwt token
    def time_remaining(self) -> timedelta:
        """Get the remaining time before the client expires"""
        return self.auth_token.time_remaining()
    
    # checking jwt token
    def _check_token_validity(self) -> None:
        """Check if the token is still valid, raise exception if expired"""
        if not self.auth_token.is_valid():
            raise Exception("Client session has expired. Please authenticate again.")
    
    def _get_token(self) -> str:
        """Get the authentication token"""
        self._check_token_validity()
        return self.auth_token._token
    
    def _make_authenticated_request(self, endpoint: str, data: Dict = None, method: str = "POST") -> Dict:
        """Make an authenticated request to the API"""
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method.upper() == "POST" and data:
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers)
            else:
                response = requests.request(method, url, json=data, headers=headers)
                
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def retrieve_spec(self, data: Dict) -> Dict:
        """
        Get specification for a single parameter
        
        Args:
            data: Dict with spec parameters containing: 
                  project, componentType, testType, stage, parameter
            
        Returns:
            Dict containing the specification data
            
        Example:
            client.retrieve_spec({'project': 'P', 'componentType': 'PCB', 
                                 'testType': 'METROLOGY', 'stage': 'PCB_RECEPTION', 
                                 'parameter': 'BOW1'})
        """
        required_fields = ['project', 'componentType', 'testType', 'stage', 'parameter']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in data: {missing_fields}")
        
        return self._make_authenticated_request("/spec", data)

    def retrieve_spec_list(self, data: Dict) -> Dict:
        """
        Get specifications for multiple parameters
        
        Args:
            data: Dict with spec parameters containing: 
                  project, componentType, testType, stage
            
        Returns:
            Dict containing the specification list data
            
        Example:
            client.retrieve_spec_list({'project': 'P', 'componentType': 'PCB', 
                                      'testType': 'METROLOGY', 'stage': 'PCB_RECEPTION'})
        """
        required_fields = ['project', 'componentType', 'testType', 'stage']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in data: {missing_fields}")
        
        return self._make_authenticated_request("/speclist", data)
    
    def health_check(self) -> Dict:
        """Check API server status"""
        return self._make_authenticated_request("/health", method="GET")

#################
### OLD FUNCTIONS - Updated to use ITKSpecClient ###
#################

#### authenticate user - now returns ITKSpecClient using new pattern
def authenticate_user(accessCode1: str, accessCode2: str):
    """Legacy function - authenticates and returns a client"""
    auth_token = authenticate(accessCode1, accessCode2)
    return ITKSpecClient(auth_token)

### get single spec - updated to use token-based authentication
def retrieve_spec(client_or_ACs, data: Dict[str, str] = None):
    """
    Get specification for a single parameter - supports both new and legacy usage
    
    Args:
        client_or_ACs: Either ITKSpecClient instance or dict with access codes
        data: Dict with spec parameters (project, componentType, testType, stage, parameter)
    
    Returns:
        Dict containing the specification data
    """
    if isinstance(client_or_ACs, ITKSpecClient):
        # New client-based usage
        client = client_or_ACs
        if data:
            return client.retrieve_spec(data)
        else:
            raise ValueError("data parameter is required")
    else:
        # Legacy usage - create client from access codes using new pattern
        ACs = client_or_ACs
        auth_token = authenticate(ACs['accessCode1'], ACs['accessCode2'])
        client = ITKSpecClient(auth_token)
        if data:
            return client.retrieve_spec(data)
        else:
            raise ValueError("data parameter is required")

### get multiple specs - updated to use token-based authentication
def retrieve_specList(client_or_ACs, data: Dict[str, str] = None):
    """
    Get specifications for multiple parameters - supports both new and legacy usage
    
    Args:
        client_or_ACs: Either ITKSpecClient instance or dict with access codes
        data: Dict with spec parameters (project, componentType, testType, stage)
    
    Returns:
        Dict containing the specification list data
    """
    if isinstance(client_or_ACs, ITKSpecClient):
        # New client-based usage
        client = client_or_ACs
        if data:
            return client.retrieve_spec_list(data)
        else:
            raise ValueError("data parameter is required")
    else:
        # Legacy usage - create client from access codes using new pattern
        ACs = client_or_ACs
        auth_token = authenticate(ACs['accessCode1'], ACs['accessCode2'])
        client = ITKSpecClient(auth_token)
        if data:
            return client.retrieve_spec_list(data)
        else:
            raise ValueError("data parameter is required")

### api help - updated to use new API
def api_help():
    """Get API help from the server"""
    base_url = DEFAULT_API_BASE_URL
    try:
        url = f"{base_url}/help"
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        print(json.dumps(result, indent=2))
        return result
    except requests.RequestException as e:
        print(f"Failed to get API help: {e}")
        return None

### server check - updated to use new API
def health_check():
    """Check API server status"""
    base_url = DEFAULT_API_BASE_URL
    try:
        url = f"{base_url}/health"
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        print(json.dumps(result, indent=2))
        return result
    except requests.RequestException as e:
        print(f"Failed to check server health: {e}")
        return None

### help
def help():
    help_text = """ITK Specifications Package Functions:

NEW RECOMMENDED USAGE:
    # Step 1: Authenticate first to get an AuthToken
    try:
        auth_token = itkspec.authenticate('your_access_code1', 'your_access_code2')
        print(f"Authentication successful. Token valid for: {auth_token.time_remaining()}")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return
    
    # Step 2: Create client with the AuthToken
    try:
        client = itkspec.ITKSpecClient(auth_token)
        print(f"Client created successfully. Valid for: {client.time_remaining()}")
    except Exception as e:
        print(f"Client creation failed: {e}")
        return
    
    # Step 3: Use the client (check validity if needed)
    if client.is_valid():
        # Get single specification using data dictionary
        spec = client.retrieve_spec({'project': 'P', 'componentType': 'PCB', 
                                    'testType': 'METROLOGY', 'stage': 'PCB_RECEPTION', 
                                    'parameter': 'BOW1'})
        print(spec)
        
        # Get multiple specifications using data dictionary
        specs = client.retrieve_spec_list({'project': 'P', 'componentType': 'PCB',
                                          'testType': 'METROLOGY', 'stage': 'PCB_RECEPTION'})
        print(specs)
        
        # Check server health
        status = client.health_check()
        print(status)
    else:
        print("Client session expired. Authenticate again.")

ALTERNATIVE SINGLE-STEP USAGE:
    # Authenticate and create client in one step (legacy-style)
    client = itkspec.authenticate_user('access_code1', 'access_code2')

LEGACY FUNCTIONS (still supported):
    1. authenticate - Get an AuthToken for creating clients
    2. authenticate_user - returns a client if the user is verified
    3. retrieve_spec - Get specification for a single parameter
    4. retrieve_specList - Get specifications for multiple parameters
    5. api_help - List the available API endpoints
    6. health_check - Check for API server status
    7. get_from_EOS - Get backup data from EOS
    8. Exit
    """
    print(help_text)

    while True:
        choice = input("Enter the number of the function you would like an example of (or type 'exit' to quit): ").strip().lower()
        if choice in ["8", "exit"]:
            print("Exiting help menu.")
            break
        details = {
            "1": "Example: auth_token = itkspec.authenticate('your_access_code1', 'your_access_code2')",
            "2": "Example: client = itkspec.authenticate_user('your_access_code1', 'your_access_code2')",
            "3": "Example: spec = itkspec.retrieve_spec(client, {'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION', 'parameter':'BOW1'})",
            "4": "Example: specs = itkspec.retrieve_specList(client, {'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION'})",
            "5": "Example: itkspec.api_help()",
            "6": "Example: itkspec.health_check()",
            "7": "Example: data = itkspec.get_from_EOS('filename.csv')",
        }
        print(details.get(choice, "Invalid selection. Please enter a number from 1 to 8."))

### data backup from EOS
def get_from_EOS(filename):
    url = f'https://eddossan.web.cern.ch/itk-specs/{filename}'
    reqs = requests.get(url)
    if reqs.status_code != 200:
        print(f"Failed to retrieve the URL: {url}")
        return []
    csv_content = reqs.text
    print(f"Fetched content from {url}:\n{csv_content[:500]}...")

    # Parse the CSV content
    data = []
    csv_reader = csv.reader(StringIO(csv_content))
    headers = ["project", "componentType", "testType", "stage", "parameter", "spec"]
    for row in csv_reader:
        if row:
            row_data = {headers[i]: row[i] for i in range(len(headers))}
            if row_data["spec"]:
                try:
                    row_data["spec"] = json.loads(row_data["spec"].replace("'", "\""))  # Convert spec string to dictionary
                except json.JSONDecodeError:
                    print(f"Failed to decode spec: {row_data['spec']}")
                    row_data["spec"] = {}
            else:
                row_data["spec"] = {}
            data.append(row_data)

    print(f"Data: {data}")
    return data