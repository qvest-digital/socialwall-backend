import json
import random
import string
from datetime import timezone
from pathlib import Path


class Util:

    @staticmethod
    def get_credentials_folder(__file__) -> Path:
        """Returns project root folder."""
        return Path(__file__).parent

    @staticmethod
    def convert_date_to_UTC_time_stamp(dt):
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    @staticmethod
    def get_json_file_from_file_path(json_file_path):
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)

        return json_data

    @staticmethod
    def randomString(stringLength=20):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))
