import base64
import uuid

class PasswordReset:
    reset_code = ''
    reset_token = ''
    token = ''

    def __init__(self):
        PasswordReset.generate_reset_token(self)

    def generate_reset_token(self):
        random_id_1 = str(uuid.uuid4())
        random_id_2 = str(uuid.uuid4())
        random_id_3 = str(uuid.uuid4())

        self.reset_code = random_id_1 + '-' + random_id_2 + '-' + random_id_3
        bytes_code = self.reset_code.encode('utf-8')
        bytes_reset_token = base64.urlsafe_b64encode(bytes_code)
        self.reset_token = bytes_reset_token.decode()

    @classmethod
    def decode_reset_token(cls, received_reset_token):
        decoded_token = base64.urlsafe_b64decode(received_reset_token)
        cls.token = decoded_token.decode()
