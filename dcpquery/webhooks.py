"""
This module serves as a script to install and manage DSS subscriptions for the service.
"""

import os, sys, argparse, json, logging, secrets

import boto3
from hca.dss import DSSClient
from dcplib.aws import clients

from . import config


def update_webhooks(action, replica, callback_url):
    dss = config.dss_client
    secret_id = f"{os.environ['APP_NAME']}/{os.environ['STAGE']}/webhook-auth-config"
    try:
        res = clients.secretsmanager.get_secret_value(SecretId=secret_id)
        keys = json.loads(res["SecretString"])["hmac_keys"]
        active_key_id = json.loads(res["SecretString"])["active_hmac_key"]
    except clients.secretsmanager.exceptions.ResourceNotFoundException:
        keys, active_key_id = {}, None

    if action == "install":
        for subscription in dss.get_subscriptions(replica=replica, subscription_type="jmespath")["subscriptions"]:
            if active_key_id != subscription["hmac_key_id"]:
                continue
            if callback_url != subscription["callback_url"]:
                continue
            if replica != subscription["replica"]:
                continue
            print("Matching subscription found, nothing to do")
            break
        else:
            print("Registering new subscription with", dss.host)
            if active_key_id is None:
                new_key_id = os.environ['STAGE'] + "-" + secrets.token_hex(8)
                keys[new_key_id] = secrets.token_urlsafe(32)
                clients.secretsmanager.put_secret_value(SecretId=secret_id,
                                                        SecretString=json.dumps({"hmac_keys": keys,
                                                                                 "active_hmac_key": new_key_id}))
            res = clients.secretsmanager.get_secret_value(SecretId=secret_id)
            webhook_keys = json.loads(res["SecretString"])["hmac_keys"]
            hmac_key_id = json.loads(res["SecretString"])["active_hmac_key"]
            res = dss.put_subscription(replica=replica,
                                       callback_url=callback_url,
                                       hmac_key_id=hmac_key_id,
                                       hmac_secret_key=webhook_keys[hmac_key_id])
            print(res)
    elif action == "remove":
        num_deleted = 0
        for subscription in dss.get_subscriptions(replica=replica, subscription_type="jmespath")["subscriptions"]:
            if callback_url != subscription["callback_url"]:
                continue
            if replica != subscription["replica"]:
                continue
            res = dss.delete_subscription(replica=replica, subscription_type="jmespath", uuid=subscription["uuid"])
            print("Deleted subscription {}: {}".format(subscription["uuid"], res))
            num_deleted += 1
        print(f"Done. Deleted {num_deleted} subscriptions.")


if __name__ == "__main__":
    config.configure_logging()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices={"install", "remove"})
    parser.add_argument("--replica", choices={"aws", "gcp"}, default="aws")
    parser.add_argument("--callback-url", required=True)
    args = parser.parse_args(sys.argv[1:])
    update_webhooks(**vars(args))
