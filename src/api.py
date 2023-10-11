"""Generator plugin for Stable Diffusion running on replicate.com."""
import json
import logging
import time
from enum import Enum
from typing import Any, Dict, Type, Union

from pydantic import Field
from steamship import Block, MimeTypes, Steamship, SteamshipError, Task, TaskState
from steamship.invocable import Config, InvocableResponse, InvocationContext
from steamship.plugin.generator import Generator
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest
from steamship.data.block import BlockUploadType
import requests,base64


BASE_URL = "https://api.getimg.ai/v1/stable-diffusion/text-to-image"

class ModelVersionEnum(str, Enum):
    """Models supported by the plugin."""
    default = ""

    @classmethod
    def list(cls):
        """List all supported model versions sizes."""
        return list(map(lambda c: c.value, cls))


def task_status_response(state: TaskState, message, prediction_id: str) -> InvocableResponse:
    """Build a response object with a TaskState and message for a given transcription_id."""
    return InvocableResponse(
        status=Task(
            state=state,
            remote_status_message=message,
            remote_status_input={"prediction_id": prediction_id},
        )
    )


class GetimgPlugin(Generator):
    """**Example** plugin for generating images from text with Getimg.ai

    The plugin accepts the following **runtime** params:
    - prompt: the input prompt for the model
    """

    class GetimgPluginConfig(Config):
        """Configuration for the Stable Diffusion Plugin."""

        api_key: str = Field(
            "",
            description="API key to use for Getimg.ai.",
        )
        base_url: str = Field(
            "",
            description="API url for Getimg.ai.",
        )


    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return configuration template for the generator."""
        return cls.GetimgPluginConfig

    config: GetimgPluginConfig

    def __init__(
        self,
        client: Steamship = None,
        config: Dict[str, Any] = None,
        context: InvocationContext = None,
    ):
        super().__init__(client, config, context)

    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        """Run the image generator against all the text, combined."""
        if self.config.base_url == "":
            self.config.base_url = BASE_URL

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        options = request.data.options        
        prompt = " ".join([block.text for block in request.data.blocks if block.text is not None])
        if not options:
            options = {}

        data = {
            "prompt": prompt,
            "model": options.get("model","realistic-vision-v3"),
            "negative_prompt": options.get("negative_prompt","disfigured, cartoon, blurry"),
            "width": options.get("width",384),
            "height": options.get("height",384),
            "steps": options.get("steps",10),
            "guidance": options.get("guidance",7.5),
            "scheduler": options.get("scheduler","dpmsolver++"),
            "output_format": "png"
        }

        response = requests.post(self.config.base_url, headers=headers, json=data)
        response_json = response.json()
        #logging.warning(response_json)
        if response.status_code == 200:
            encoded_image = response_json["image"]
            decoded_image = base64.b64decode(encoded_image)
        else:
            decoded_image = None  # Set a default value if the response status code is not 200

        blocks = []
        if decoded_image is not None:
            blocks.append(Block(upload_bytes=decoded_image, mime_type=MimeTypes.PNG, upload_type=BlockUploadType.FILE))

        return InvocableResponse(data=RawBlockAndTagPluginOutput(blocks=blocks))


#if __name__ == "__main__":

    #getimg = GetimgPlugin()
    #request = PluginRequest(
    #    data=RawBlockAndTagPluginInput(blocks=[Block(text="spaceman")])
    #)
    #response = getimg.run(request)
    #print(str(response))
 
    