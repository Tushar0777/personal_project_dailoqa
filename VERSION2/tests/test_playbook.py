import boto3 
import pytest
# import moto as mock_dynamodb
from moto import mock_aws
from app.crud import create_playbook,create_new_version,get_latest_version
from botocore.exceptions import ClientError


# version2 se jake pytest -v chala vrna ye app wale forder ko aise ignore krta hai 
@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
        table = dynamodb.create_table(
            TableName="Playbooks",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        table.wait_until_exists()
        yield table


def test_create_playbook_success(dynamodb_table):
    playbook_id="playbook1"
    create_playbook(dynamodb_table,playbook_id)

    response = dynamodb_table.get_item(
        Key={
            "PK": playbook_id,
            "SK": "META"
        }
    )

    item = response["Item"]

    assert item["PK"] == playbook_id
    assert item["SK"] == "META"
    assert item["latestVersion"] == 0
    assert item["totalVersions"] == 0
    assert "createdAt" in item
    assert "updatedAt" in item


def test_create_playbook_duplicate_fails(dynamodb_table):
    playbook_id = "playbook1"

    create_playbook(dynamodb_table,playbook_id)

    with pytest.raises(ClientError) as exc:
        create_playbook(dynamodb_table,playbook_id)

    assert exc.value.response["Error"]["Code"] == "ConditionalCheckFailedException"




def test_create_new_version_success(dynamodb_table):
    playbook_id="playbook1"
    create_playbook(dynamodb_table,playbook_id)

    create_new_version(
        table=dynamodb_table,
        playbook_id="playbook1",
        content="version 1 content"
    )


    meta = dynamodb_table.get_item(
        Key={"PK": "playbook1", "SK": "META"}
    )["Item"]

    assert meta["latestVersion"] == 1
    assert meta["totalVersions"] == 1

    version = dynamodb_table.get_item(
        Key={"PK": "playbook1", "SK": "VERSION#1"}
    )["Item"]

    assert version["version"] == 1
    assert version["content"] == "version 1 content"
    assert "createdAt" in version

def test_create_multiple_versions(dynamodb_table):
    playbook_id="playbook1"
    create_playbook(dynamodb_table,playbook_id)
    create_new_version(dynamodb_table, "playbook1", "v1")
    create_new_version(dynamodb_table, "playbook1", "v2")

    meta = dynamodb_table.get_item(
        Key={"PK": "playbook1", "SK": "META"}
    )["Item"]

    assert meta["latestVersion"] == 2
    assert meta["totalVersions"] == 2

# def test_get_latest_version(dynamodb_table):
#     playbook_id="playbook1"
#     create_playbook(dynamodb_table,playbook_id)

def test_get_latest_version(dynamodb_table):
    playbook_id="playbook1"
    create_playbook(dynamodb_table,playbook_id)
    create_new_version(dynamodb_table, "playbook1", "v1")
    create_new_version(dynamodb_table, "playbook1", "v2")

    latest = get_latest_version(dynamodb_table, "playbook1")

    assert latest["version"] == 2
    assert latest["content"] == "v2"
