import os

import httpx
from timbal import Agent
from timbal.core.shared import RemoteConfig
from timbal.types import Message


ORG_ID = "10"
# KB_ID = "56"
# TABLE_NAME = "leads"
CHATBOT_APP_ID = "32"
SCORING_APP_ID = "93"


agent = Agent(remote_config=RemoteConfig(
    org_id=ORG_ID,
    app_id=SCORING_APP_ID,
))


async def get_thread(
    org_id: str,
    app_id: str,
    thread_id: str,
):
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {os.getenv('TIMBAL_API_TOKEN')}",
        }
        res = await client.get(
            f"https://dev.timbal.ai/orgs/{org_id}/apps/{app_id}/threads/{thread_id}",
            headers=headers,
        )
        res.raise_for_status()
        return res.json()


def parse_thread_messages(thread: dict):
    messages = []
    for run in thread["thread"]["data"]["messages"]: # TODO I need to change this key to runs
        messages.append(Message.validate(run["message"]))
    return messages


async def main():
    thread = await get_thread(
        org_id=ORG_ID,
        app_id=CHATBOT_APP_ID,
        thread_id="15662",
    )
    messages = parse_thread_messages(thread)
    
    # Stream the events instead of using complete
    print("Starting streaming...")
    async for event in agent.run(prompt=messages):
        print(f"Event: {event}")
    print("Streaming finished.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    