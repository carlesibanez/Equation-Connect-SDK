
# EquationConnectSDK

This is an unofficial Python package to interact with and control Equation radiators from Leroy Merlin, that use the EquationConnect app. It is based on the [equation-conect.js JavaScript library](https://github.com/AndreMiras/equation-connect.js) by AndreMiras, from where the API configuration parameters and endpoints have been extracted. The package can be easily installed through pip using the following command:

```python
python3 -m pip install EquationConnectSDK
```

Once installed you just need to import it to start using it. Some examples can be found on the [demo](demo.ipynb) file.


## API Reference

Here is the documentation for the different endpoints that are implemented in the SDK to retreive information from the devices, as well as to modify their properties such as power state or target temperature. Before being able to make calls to the Firebase API, one needs to login using the [Firebase Auth REST API](https://firebase.google.com/docs/reference/rest/auth). From the response, the `idToken` and the `localId` will be needed for the future calls. Notice that the `idToken` needs to be included as a parameter and not as a header.

Here are all the parameters common to all the methods:

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `DATABASE_URL` | `string` | **Required**. This is the URL for the firebase database. |
| `FIREBASE_TOKEN` | `string` | **Required**. This is the idToken retreived after loging in. |


### Get user information

```http
  <DATABASE_URL>users/<UID>.json?auth=<FIREBASE_TOKEN>
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `UID` | `string` | This is the localId from the login, it is the user id. |   

### Get user installations

```http
  <DATABASE_URL>installations2.json?auth=<FIREBASE_TOKEN>&orderBy="userid"&equalTo="<UID>"
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `UID` | `string` | This is the localId from the login, it is the user id. | 

### Get zone for an installation

```http
  <DATABASE_URL>installations2/<InstallationId>/zones/<ZoneId>.json?auth=<FIREBASE_TOKEN>
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `InstallationId` | `string` | This is an Installation ID, can be obtained when listing user installations. | 
| `ZoneId` | `string` | This is a Zone ID, can be obtained when listing user installations. Needs to be a zone in the installation. | 

### Get device properties

```http
  <DATABASE_URL>devices/<DeviceId>.json?auth=<FIREBASE_TOKEN>
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `DeviceId` | `string` | This is an ID for a specific device, can be obtained when listing installations or for a specific zone. | 


### Set device properties

This endpoint is the same for changing any property by specifying it in the request body, i.e. changing the temperature, changing preset or turning on/off the radiator.

```http
  # Endpoint
  <DATABASE_URL>devices/<DeviceId>/data.json?auth=<FIREBASE_TOKEN>

  # For example to turn on, this would be the body:
  {
    "power": true
  }

```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `DeviceId` | `string` | This is an ID for a specific device, can be obtained when listing installations or for a specific zone. | 

## Acknowledgements

 - [equation-conect.js](https://github.com/AndreMiras/equation-connect.js)


