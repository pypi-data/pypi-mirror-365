import requests
import urllib3
from urllib.parse import urljoin
import warnings
import time
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter("ignore", category=urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logger = logging.getLogger("cccAPI")

class cccAPIConnection:
    def __init__(self, base_url, username, password, max_retries=3, retry_delay=1, 
                 connection_timeout=10, disable_connection_pooling=False):
        """
        Initialize the CCC connection client.

        :param base_url: The base URL of the CCC API (e.g., "https://localhost:8080")
        :param username: The username to be used for authentication CCC username (e.g. root)
        :param password: The password for authentication (or an application password)
        :param max_retries: Maximum number of retry attempts for failed requests
        :param retry_delay: Base delay in seconds between retries (will use exponential backoff)
        :param connection_timeout: Connection timeout in seconds
        :param disable_connection_pooling: If True, disable connection pooling to prevent connection reuse issues
        """
        self.base_path = "/cmu/v1/"
        self.base_url = base_url.rstrip("/") + self.base_path
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with 'http://' or 'https://'")
        self.username = username
        self.password = password
        self.session_id = None
        self.csrf_token = None
        self.validity = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_timeout = connection_timeout
        self.disable_connection_pooling = disable_connection_pooling
        
        # Create a session for connection reuse
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        
        # Configure adapter with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=1 if disable_connection_pooling else 10,
            pool_maxsize=1 if disable_connection_pooling else 10
        )
        
        # Mount the adapter to both HTTP and HTTPS
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set timeout
        self.session.timeout = connection_timeout
        
        # Authenticate upon initialization
        self._authenticate()

    def _authenticate(self):
        """Authenticate with the CCC API Server and store X-Auth-Token and validity.
        
        Retries up to max_retries times with exponential backoff before raising an exception.
        """
        auth_url = urljoin(self.base_url, "sessions")
        payload = {"login": self.username, 
                   "password": self.password}
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Authentication to {auth_url} attempt {attempt}/{self.max_retries}")
                response = self.session.post(auth_url, json=payload, verify=False, timeout=self.connection_timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    print(data)
                    if "token" in data:
                        self.x_auth_token=data["token"]["code"]
                        self.session_validity=data["token"]["validity"]
                        logger.debug("Authentication successful")
                        return  # Successful authentication
                    else:
                        last_exception = Exception("Authentication failed: Invalid session response")
                else:
                    # Try to extract an error message from the response
                    try:
                        #error_msg = response.json().get("error", {}).get("message", "Unknown error")
                        error_msg = response.json()
                    except (json.decoder.JSONDecodeError, ValueError):
                        error_msg = f"HTTP {response.status_code}: {response.reason}"
                    last_exception = Exception(f"Authentication failed: {error_msg}")
            except Exception as e:
                last_exception = e
                logger.warning(f"Authentication attempt {attempt} failed: {str(e)}")

            if attempt < self.max_retries:
                # Calculate exponential backoff delay
                current_delay = self.retry_delay * (2 ** (attempt - 1))
                logger.debug(f"Retrying authentication in {current_delay} seconds...")
                time.sleep(current_delay)

        # All attempts failed; raise the last captured exception.
        logger.error(f"All authentication attempts failed: {str(last_exception)}")
        raise last_exception

    def _get_headers(self):
        """Return headers including the authentication X-Auth-Token and Validity."""
        if not self.x_auth_token or not self.session_validity:
            self._authenticate()

        return {
            "X-Auth-Token": self.x_auth_token,
            "validity": self.session_validity
        }

    def _do_call(self, method, endpoint, params=None, data=None, files=None, is_binary=False):
        """Internal method to send an authenticated request to the cccAPI Server."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        # Convert dictionary to form-encoded string if sending multipart
        request_data = None if files else data
        form_data = data if files else None  # Ensure correct encoding

        try:
            logger.debug(f"Sending {method} request to {url}")
            response = self.session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=request_data,
                files=files,
                data=form_data,
                verify=False,
                timeout=self.connection_timeout
            )

            if response.status_code == 401:
                logger.warning("Session expired, re-authenticating")
                self._authenticate()
                headers = self._get_headers()
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=request_data,
                    files=files,
                    data=form_data,
                    verify=False,
                    timeout=self.connection_timeout
                )

            # Handle 4xx responses gracefully
            if 400 <= response.status_code < 500:
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    return {"error": f"HTTP {response.status_code}: {response.reason}"}

            response.raise_for_status()

            if is_binary:
                return response.content  # Return raw binary content (e.g., for file exports)

            if not response.content.strip():
                return {}  # Handle empty response

            try:
                return response.json()  # Attempt to parse JSON
            except requests.exceptions.JSONDecodeError:
                return response.text  # Return raw text as fallback
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise Exception(f"Connection error: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timed out: {str(e)}")
            raise Exception(f"Request timed out: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Request error: {str(e)}")

    def get(self, endpoint, params=None, is_binary=False):
        """Send a GET request."""
        return self._do_call("GET", endpoint, params=params, is_binary=is_binary)

    def post(self, endpoint, data=None, files=None):
        """Send a POST request."""
        return self._do_call("POST", endpoint, data=data, files=files)

    def put(self, endpoint, data=None):
        """Send a PUT request."""
        return self._do_call("PUT", endpoint, data=data)

    def delete(self, endpoint, params=None, data=None):
        """Send a DELETE request."""
        return self._do_call("DELETE", endpoint, params=params, data=data)

    def patch(self, endpoint, data=None):
        """Send a PATCH request."""
        return self._do_call("PATCH", endpoint, data=data)
    
    def exit(self):
        """Delete the current session and close connections."""
        try:
            response = self.delete("session")
        except Exception as e:
            logger.warning(f"Error during session exit: {str(e)}")
            response = {"error": str(e)}
        finally:
            # Clear stored session info
            #self.session_id = None

            self.x_auth_token = None
            self.session_validity = None
            
            # Close the session to release connections
            self.session.close()

        return response