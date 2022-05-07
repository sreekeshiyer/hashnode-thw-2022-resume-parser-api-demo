from botocore.config import Config

boto_config = Config(
        region_name = 'ap-south-1',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )