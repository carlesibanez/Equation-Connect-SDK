import pyrebase

class EquationConnectAPI:
    def __init__(self, email, password):
        # Firebase configuration
        self.config = {
            "apiKey": "AIzaSyDfqBq3AfIg1wPjuHse3eiXqeDIxnhvp6U",
            "authDomain": "oem1-elife-cloud-prod.firebaseapp.com",
            "databaseURL": "https://oem2-elife-cloud-prod-default-rtdb.firebaseio.com",
            "projectId": "oem2-elife-cloud-prod",
            "storageBucket": "oem2-elife-cloud-prod.appspot.com",
            "appId": "1:150904115315:android:03aeef2c831bbda0061a06",
        }
        # Initialize Firebase
        self.firebase = pyrebase.initialize_app(self.config)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()
        # Authenticate user
        self.email = email
        self.password = password
        self.user = self._authenticate()
        self.id_token = self.user['idToken']
        self.uid = self.user['localId']

    def _authenticate(self):
        try:
            user = self.auth.sign_in_with_email_and_password(self.email, self.password)
            print("Authenticated successfully")
            return user
        except Exception as e:
            print("Authentication failed:", e)
            return None

    def refresh_token(self):
        """Refresh the user's token, which may expire after an hour."""
        try:
            self.user = self.auth.refresh(self.user['refreshToken'])
            self.id_token = self.user['idToken']
            print("Token refreshed successfully")
        except Exception as e:
            print("Token refresh failed:", e)

    def get_user_info(self):
        """Retrieve user information."""
        return self.db.child("users") \
                      .child(self.uid) \
                      .get(self.id_token).val()

    def get_installations(self):
        """Retrieve installations associated with the user's UID."""
        installations = self.db.child("installations2") \
            .order_by_child("userid") \
            .equal_to(self.uid) \
            .get(self.id_token)
        return installations.val()

    def get_zone(self, installation_id, zone_id):
        """Retrieve specific zone information for a given installation."""
        return self.db.child("installations2").child(installation_id).child("zones").child(zone_id).get(self.id_token).val()

    def get_device(self, device_id):
        """Retrieve specific device information."""
        return self.db.child("devices").child(device_id).get(self.id_token).val()

    def set_device_power(self, device_id, power_state: bool):
        """Update the power state of a device (on/off)."""
        data = {"power": power_state}
        return self.db.child("devices").child(device_id).child("data").update(data, self.id_token)

    def set_device_temperature(self, device_id, temperature: int):
        """Update the temperature setting of a device."""
        data = {"temp": temperature}
        return self.db.child("devices").child(device_id).child("data").update(data, self.id_token)

    def set_device_mode(self, device_id, mode: str):
        """Set the device mode (e.g., 'manual' or 'eco')."""
        data = {"mode": mode}
        return self.db.child("devices").child(device_id).child("data").update(data, self.id_token)

