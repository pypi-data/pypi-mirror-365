from strands import Agent
from strands.models import BedrockModel

from strands import tool

__all__ = ["run"]

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    # model_id="us.amazon.nova-micro-v1:0",
    region_name='us-east-1',
)


def run():
    agent = Agent(model=bedrock_model)
    agent("こんにちは")

