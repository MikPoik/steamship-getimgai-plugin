"""Tool for generating images. Moved from tools folder because template import issues"""
from typing import List, Union, Any
from steamship.agents.schema import AgentContext  #upm package(steamship)
from steamship.agents.tools.base_tools import ImageGeneratorTool  #upm package(steamship)
from steamship.utils.repl import ToolREPL  #upm package(steamship)
from steamship import Block, Steamship, Task  #upm package(steamship)
import logging


class SelfieTool(ImageGeneratorTool):

  name: str = "selfie_tool"
  human_description: str = "Generates a selfie-style image from text with getimg.ai"
  agent_description = (
      "Useful to generate images from text prompts. Only use if the human is currently requesting for a selfie or image or picture, etc. The input should be a plain text string of comma separated keywords, that describes in detail, the image."
  )

  generator_plugin_handle: str = "getimg-ai"
  generator_plugin_config: dict = {"api_key": "key-"}
  url = "https://api.getimg.ai/v1/stable-diffusion/text-to-image"

  def run(self,
          tool_input: List[Block],
          context: AgentContext,
          api_key: str = "") -> Union[List[Block], Task[Any]]:

    current_model = "realistic-vision-v3"
    #current_model = "dark-sushi-mix-v2-25"
    current_negative_prompt = "disfigured, cartoon, blurry"

    image_generator = context.client.use_plugin(
        plugin_handle=self.generator_plugin_handle,
        config=self.generator_plugin_config,
        version="0.0.7")
    options = {
        "model": current_model,
        "width": 512,
        "height": 768,
        "steps": 25,
        "guidance": 7.5,
        "negative_prompt": current_negative_prompt
    }

    prompt = tool_input[0].text

    #logging.warning("Getimg prompt: "+prompt)
    task = image_generator.generate(
        text=prompt,
        make_output_public=True,
        append_output_to_file=True,
        options=options,
    )
    task.wait()
    blocks = task.output.blocks
    output_blocks = []

    for block in blocks:
      output_blocks.append(block)
    return output_blocks


if __name__ == "__main__":
  print("Try running with an input like 'penguin'")
  ToolREPL(SelfieTool()).run()
