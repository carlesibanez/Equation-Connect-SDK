import time
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

class API:
    def __init__(self, email, password, session: aiohttp.ClientSession):
        self.email = email
        self.password = password
        self.session = session # Store the async session
        
        # API and database configuration
        self.api_key = "AIzaSyDfqBq3AfIg1wPjuHse3eiXqeDIxnhvp6U"
        self.database_url = "https://oem2-elife-cloud-prod-default-rtdb.firebaseio.com"
        
        # Parameters for authentication
        self.user = None
        self.id_token = None
        self.uid = None
        self.token_expiration = 0

    async def authenticate(self):
        """Authenticate with Google Identity Toolkit to get a token."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        payload = {
            "email": self.email,
            "password": self.password,
            "returnSecureToken": True
        }
        
        try:
            async with self.session.post(url, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    _LOGGER.error(f"Auth failed: {resp.status} - {error_text}")
                    return None
                
                data = await resp.json()
                
                # Save the results exactly like Pyrebase did
                self.user = data
                self.id_token = data['idToken']
                self.uid = data['localId']
                expires_in = int(data.get('expiresIn', 3600))
                self.token_expiration = time.time() + expires_in
                
                _LOGGER.info("Authenticated successfully")
                return self.user

        except Exception as e:
            _LOGGER.error(f"Authentication exception: {e}")
            return None

    async def refresh_token(self):
        """Refresh the user's token using the saved refresh token."""
        url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        
        # We need the refresh token we got during login
        refresh_token = self.user.get('refreshToken')
        if not refresh_token:
            _LOGGER.error("Cannot refresh token: No refresh token found.")
            return

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        try:
            async with self.session.post(url, json=payload) as resp:
                if resp.status != 200:
                    _LOGGER.error("Token refresh failed.")
                    return
                
                data = await resp.json()
                
                # Update our local state
                self.id_token = data['id_token'] # Note: Google returns 'id_token' here (underscore), not 'idToken'
                self.user['idToken'] = data['id_token']
                self.user['refreshToken'] = data['refresh_token'] # Update it for next time
                
                expires_in = int(data.get('expires_in', 3600))
                self.token_expiration = time.time() + expires_in
                _LOGGER.info("Token refreshed successfully")

        except Exception as e:
            _LOGGER.error(f"Token refresh exception: {e}")

    async def ensure_token_valid(self):
        """Check if token is expired (or close to it) and refresh if needed."""
        # Refresh if token expires in less than 5 minutes (300 seconds)
        if time.time() >= self.token_expiration - 300:
            await self.refresh_token()

    async def _request(self, method, path, json_data=None, params=None):
        """Internal helper to handle Firebase Database requests."""
        await self.ensure_token_valid()

        url = f"{self.database_url}/{path}.json"
        
        # 1. Start with the auth token
        request_params = {"auth": self.id_token}
        
        # 2. Add any specific query parameters (like orderBy)
        if params:
            request_params.update(params)

        try:
            # Pass 'params' to aiohttp. It handles the ?key=value formatting automatically
            async with self.session.request(method, url, json=json_data, params=request_params) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    _LOGGER.error(f"Request failed: {method} {path} - {resp.status} - {text}")
                    return None
                
                return await resp.json()
        except Exception as e:
            _LOGGER.error(f"Request exception: {e}")
            return None

    # --- GETTERS ---

    async def get_user_info(self):
        """Retrieve user information."""
        return await self._request("GET", f"users/{self.uid}")

    async def get_installations(self):
        """Retrieve installations associated with the user's UID (Server-Side Filter)."""
        
        # Equivalent to Pyrebase:
        # .order_by_child("userid").equal_to(self.uid)
        
        # NOTE: Firebase REST requires the values to be JSON-encoded strings.
        # This means we must wrap the keys and values in double quotes.
        query_params = {
            "orderBy": '"userid"',       # Must be '"userid"', not 'userid'
            "equalTo": f'"{self.uid}"'   # Must be '"uid_value"', not 'uid_value'
        }

        # This will now only return the specific records for this user
        data = await self._request("GET", "installations2", params=query_params)
        
        if not data:
            return {}
            
        return data

    async def get_device(self, device_id):
        """Retrieve specific device information."""
        return await self._request("GET", f"devices/{device_id}")

    async def get_devices(self):
        """Retrieve all devices associated with the user."""
        _LOGGER.debug("Fetching devices for user.")
        installations = await self.get_installations()
        if not installations:
            return []

        devices = []
        for inst_id, inst_data in installations.items():
            zones = inst_data.get("zones", {})
            for zone_id, zone_data in zones.items():
                device_ids = zone_data.get("devices", {}).keys()
                
                # Optimization: We could fetch all devices in one go if the list is small,
                # but following your old logic, we fetch one by one.
                for dev_id in device_ids:
                    device = await self.get_device(dev_id)
                    if device:
                        # Add the ID to the device object so we know which one it is
                        device['id'] = dev_id 
                        devices.append(device)
        return devices

    # --- SETTERS ---

    async def set_device_power(self, device_id, power_state: bool):
        """Update the power state."""
        # .update() in Pyrebase = PATCH in REST
        path = f"devices/{device_id}/data"
        payload = {"power": power_state}
        return await self._request("PATCH", path, json_data=payload)

    async def set_device_temperature(self, device_id, temperature: int):
        """Update the temperature."""
        path = f"devices/{device_id}/data"
        payload = {"temp": temperature}
        return await self._request("PATCH", path, json_data=payload)

    async def set_device_mode(self, device_id, mode: str):
        """Set the device mode."""
        path = f"devices/{device_id}/data"
        payload = {"mode": mode}
        return await self._request("PATCH", path, json_data=payload)

