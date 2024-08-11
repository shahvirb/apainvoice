from apainvoice import db
import datetime
import logging

logger = logging.getLogger(__name__)

DEFAULT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjVyTjd2TDlFOUlwWUlnTjJsQ0JMdFd0TnhBZXRYaHkxNUJwNzl4a18wOVEifQ.eyJhcHBsaWNhdGlvblJlZnJlc2hUb2tlbklkIjoiNDY5NDM1NiIsImlhdCI6MTcyMjQ2Mzc1MywiaXNzIjoiQVBBIiwic3ViIjoiMjI3ODQ5MyJ9.POx2fQMK1ZkGK87aSjZxCJ45UVg01r-IvtzLnahNCXu4SzKEMfgX7cRnUiLqQhbmsq6-kiYclJBfZDcDhc6EMrspR30Y4CgqyJoSPW1_sSDSi7xUs4UP6Rjo4mqVdmAgc25qHUjDGDIzIikTjsQFCr6YzEpt600G4Vtskl9ZyRPYoi9h_CM8i_alXywepK9L4YALIq2pw08ePZSy5dMVqeVYOqkXBByQBfgV-UAnbA5LTrwbtVqMrfQ5RfyfwaOBnuwh2tKxr-wBa2Nb_WoFK3cYrSmkEMxUSwk-ps0kyKPG2qYmTIIc5FaodO4vXAoOG27FcsNTnUj4cGR6eebRFA"


class AccessToken:
    def __init__(self, default_token=DEFAULT_TOKEN) -> None:
        try:
            with db.get_db() as conn:
                conn["access_token"]["token"]
        except KeyError:
            self.token = DEFAULT_TOKEN

    @property
    def token(self) -> str:
        with db.get_db() as conn:
            return conn["access_token"]["token"]

    @token.setter
    def token(self, t) -> None:
        with db.get_db() as conn:
            ctime = datetime.datetime.now()
            conn["access_token"] = {"token": t, "created": ctime}
            logger.debug(f'Wrote access token @ {ctime}')


if __name__ == "__main__":
    at = AccessToken()
    print(at.token)
    with db.get_db() as d:
        print(d["access_token"]["created"])
