import os
import pathlib
import requests
import sys

from cappa import command
from dataclasses import dataclass

__all__ = ["TGCSRelease"]


@command(name="release")
@dataclass
class TGCSRelease:
    do_release: bool = False
    version: str = "latest"
    bundle_path: pathlib.Path = pathlib.Path("bundle.zip")

    def __call__(self):
        api_url = os.environ["TGCS_SERVER"].rstrip("/")

        token_url = os.environ["AUTH0_URL"].rstrip("/") + "/oauth/token"
        client_id = os.environ["AUTH_M2M_CLIENT_ID"]
        client_secret = os.environ["AUTH_M2M_CLIENT_SECRET"]
        auth_aud = os.environ["AUTH_AUDIENCE"]

        tgcs_token_req = requests.post(
            token_url,
            headers={"Content-Type": "application/json"},
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
                "audience": auth_aud,
            },
        )

        if not tgcs_token_req.ok:
            print(f"Error: encountered while obtaining token; {tgcs_token_req.status_code} {tgcs_token_req.content}")

        tgcs_token = tgcs_token_req.json()
        tgcs_headers = {"Authorization": f"Bearer {tgcs_token['access_token']}"}

        release_req = requests.get(
            f"{api_url}/api/v1/releases/{self.version}", headers=tgcs_headers
        )

        if release_req.status_code == 404:
            print("No release found")
            exit(0)

        if release_req.status_code != 200:
            print(
                f"Error: encountered while fetching release; {release_req.content}",
                file=sys.stderr,
            )
            exit(1)

        release_data = release_req.json()

        if release_data["published_dt"] is not None:
            # Nothing to do
            print("Nothing to do", file=sys.stderr)
            exit(0)

        version = str(release_data["version"])

        if self.do_release:
            # Flag release as published on TGCS

            put_data = {
                **release_data,
                "published": True,
            }  # server will auto-fill timestamp
            r = requests.put(
                f"{api_url}/api/v1/releases/{version}",
                headers=tgcs_headers,
                json=put_data,
            )

            if r.status_code != 200:
                print(
                    f"Error: could not set published flag for version {version}; got {r.status_code}: {r.content}",
                    file=sys.stderr,
                )
                exit(1)

            print(f" Request: {put_data}")
            print(f"Response: {r.json()}")

        else:
            bundle = requests.get(
                f"{api_url}/api/v1/releases/{version}/bundle", headers=tgcs_headers
            )
            with open(self.bundle_path, "wb") as fh:
                fh.write(bundle.content)
