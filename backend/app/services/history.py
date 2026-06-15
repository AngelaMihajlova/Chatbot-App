import json
import time
import uuid
from typing import List

import boto3
import boto3.dynamodb.conditions as conditions
from botocore.config import Config as BotoConfig

_BOTO_TIMEOUT = BotoConfig(connect_timeout=5, read_timeout=10, retries={"max_attempts": 1})
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import SystemConfig


def _get_mode(db: Session) -> str:
    row = db.query(SystemConfig).filter(SystemConfig.key == "DYNAMO_MODE").first()
    return row.value if row else "local"


def get_dynamo(db: Session):
    if _get_mode(db) == "aws":
        return boto3.resource(
            "dynamodb",
            region_name=settings.AWS_DYNAMO_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return boto3.resource(
        "dynamodb",
        endpoint_url=settings.DYNAMO_LOCAL_ENDPOINT,
        region_name="us-west-2",
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
        config=_BOTO_TIMEOUT,
    )


def ensure_tables(db: Session) -> None:
    dynamo = get_dynamo(db)
    existing = dynamo.meta.client.list_tables()["TableNames"]

    if settings.DYNAMO_SESSIONS_TABLE not in existing:
        dynamo.create_table(
            TableName=settings.DYNAMO_SESSIONS_TABLE,
            KeySchema=[{"AttributeName": "session_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "session_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

    if settings.DYNAMO_MESSAGES_TABLE not in existing:
        dynamo.create_table(
            TableName=settings.DYNAMO_MESSAGES_TABLE,
            KeySchema=[
                {"AttributeName": "session_id", "KeyType": "HASH"},
                {"AttributeName": "created_at", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "session_id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "N"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )


def create_session(db: Session, user_id: str, title: str = "") -> str:
    dynamo = get_dynamo(db)
    session_id = str(uuid.uuid4())
    dynamo.Table(settings.DYNAMO_SESSIONS_TABLE).put_item(Item={
        "session_id": session_id,
        "user_id": user_id,
        "title": title,
        "created_at": int(time.time()),
    })
    return session_id


def list_sessions(db: Session, user_id: str) -> List[dict]:
    dynamo = get_dynamo(db)
    resp = dynamo.Table(settings.DYNAMO_SESSIONS_TABLE).scan(
        FilterExpression=conditions.Attr("user_id").eq(user_id)
    )
    items = resp.get("Items", [])
    return sorted(items, key=lambda x: x.get("created_at", 0), reverse=True)


def get_messages(db: Session, session_id: str) -> List[dict]:
    dynamo = get_dynamo(db)
    resp = dynamo.Table(settings.DYNAMO_MESSAGES_TABLE).query(
        KeyConditionExpression=conditions.Key("session_id").eq(session_id),
        ScanIndexForward=True,
    )
    items = resp.get("Items", [])
    for item in items:
        if isinstance(item.get("citations"), str):
            try:
                item["citations"] = json.loads(item["citations"])
            except Exception:
                item["citations"] = []
    return items


def add_message(db: Session, session_id: str, role: str, content: str, citations: list = None) -> None:
    dynamo = get_dynamo(db)
    item = {
        "session_id": session_id,
        "created_at": int(time.time() * 1000),
        "role": role,
        "content": content,
    }
    if citations:
        item["citations"] = json.dumps(citations)
    dynamo.Table(settings.DYNAMO_MESSAGES_TABLE).put_item(Item=item)


def update_session_title(db: Session, session_id: str, title: str) -> None:
    dynamo = get_dynamo(db)
    dynamo.Table(settings.DYNAMO_SESSIONS_TABLE).update_item(
        Key={"session_id": session_id},
        UpdateExpression="SET title = :t",
        ExpressionAttributeValues={":t": title},
    )


def delete_session(db: Session, session_id: str, user_id: str) -> None:
    dynamo = get_dynamo(db)
    sessions_table = dynamo.Table(settings.DYNAMO_SESSIONS_TABLE)
    messages_table = dynamo.Table(settings.DYNAMO_MESSAGES_TABLE)

    item = sessions_table.get_item(Key={"session_id": session_id}).get("Item")
    if not item or item.get("user_id") != user_id:
        raise ValueError("Session not found or access denied")

    msgs = messages_table.query(
        KeyConditionExpression=conditions.Key("session_id").eq(session_id)
    ).get("Items", [])
    for msg in msgs:
        messages_table.delete_item(Key={"session_id": session_id, "created_at": msg["created_at"]})

    sessions_table.delete_item(Key={"session_id": session_id})
