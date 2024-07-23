import json
import uuid

from thehive4py.api import TheHiveApi
from thehive4py.exceptions import AlertException
from thehive4py.models import Alert, AlertArtifact

from settings import Tags


class HiveAPI:

    def __init__(self, url, key):
        self.hive_url = url
        self.api_key = key
        self.api = TheHiveApi(self.hive_url, self.api_key)

    def make_alert(self, title, description, alert_type, artifacts, tag):
        alert_artifacts = ([AlertArtifact(dataType=data_type, data=data) for data_type, data in artifacts])
        source_ref = str(uuid.uuid4())[0:6]

        alert = Alert(title=title,
                      tags=[tag],
                      description=description,
                      type=alert_type,
                      source='IVRE',
                      sourceRef=source_ref,
                      artifacts=alert_artifacts
                      )

        self.send_alert(alert)

    def send_alert(self, alert):
        try:
            response = self.api.create_alert(alert)
            # print(json.dumps(response.json(), indent=4, sort_keys=True))

        except AlertException as e:
            print("Alert create error: {}".format(e))
