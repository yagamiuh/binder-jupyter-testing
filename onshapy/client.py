import requests, json

class OnShapeClient:
    def __init__(self, client = ""):
        self.client = client
        self.__refresh_token()

    def __refresh_token(self):
        try:
            url = "https://onshape-jupyter-extension.cyclic.app/api/get-token"
            payload= f'hash={self.client}'
            headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
            response = requests.request("POST", url, headers = headers, data = payload)
            response = json.loads(response.text)
            self.access_token = response["access_token"]
            return True
        except:
            return False

    def request(self, method, endpoint, data = None):
        url = f"https://cad.onshape.com/api/v5/{endpoint}"
        headers = {"authorization": f"Bearer {self.access_token}"}
        resp = requests.request(method, url, headers = headers, data = data)
        text = resp.text
        if "invalid_token" in text or "Unauthenticated API request" in text:
            if self.__refresh_token():
                return self.request(method, endpoint)
        else:
            try:
                return json.loads(text)
            except:
                return text

    def get(self, endpoint, **query):
        if query is not None:
            query = "&".join(list(map(lambda x: f"{x}={query[x]}", query.keys())))
            endpoint = f"{endpoint}?{query}"
        return self.request("GET", endpoint)
    
    def post(self, endpoint, body):
        payload = json.dumps(body)
        return self.request("POST", endpoint, payload)
    
    def get_document(self, id):
        return self.get(f"documents/{id}")

    def update_document(self, id, body):
        return self.post(f"documents/{id}", body)

    def get_user_session_info(self):
        return self.get(f"users/sessioninfo")

    def get_user_settings(self, id = None):
        if id is None:
            return self.get(f"users/settings")
        else:
            return self.get(f"users/{id}/settings")
    
    def get_sessions(self):
        return self.get(f"versions")
    
    def get_features(self, document, workspace, element, wvm = "w"):
        endpoint = f"partstudios/d/{document}/{wvm}/{workspace}/e/{element}/features"
        return self.get(endpoint)
    
    def update_feature(self, document, workspace, element, feature, wvm = "w"):
        update = {"feature": feature}
        featuredId = feature["featureId"]
        return self.post(f"partstudios/d/{document}/{wvm}/{workspace}/e/{element}/features/featureid/{featuredId}", update)

    def get_feature_parameter(self, feature, parameter):
        parameters = feature["parameters"]
        depthParameter = next(filter(lambda x: x["parameterId"] == parameter, parameters))
        return depthParameter

    def PartStudios(self, document, workspace, element, wvm = "w"):
        return PartStudios(self, document, workspace, element, wvm)

class PartStudios:
    def __init__(self, client, document, workspace, element, wvm = "w"):
        self.client = client
        self.document = document
        self.workspace = workspace
        self.element = element
        self.wvm = wvm

    def get_features(self, filterFunc = None):
        features = self.client.get_features(self.document, self.workspace, self.element, self.wvm)["features"]
        if filter is None:
            return features
        else:
            return list(filter(filterFunc, features))

class Feature:
    pass