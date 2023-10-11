import json
from typing import Optional

from steamship import Block, File, Steamship, MimeTypes, Tag
from steamship.data import TagKind
from steamship.data.tags.tag_constants import RoleTag
GENERATOR_HANDLE = "getimg-ai"
client = Steamship(workspace="plugin-test")
getimg = client.use_plugin(GENERATOR_HANDLE, config={"api_key":"key-"})
options = {
    "model": "realistic-vision-v3",
    "negative_prompt": "disfigured, cartoon, blurry",
    "width": 384,
    "height": 512,
    "steps": 25,
    "guidance": 7.5,
    "output_format":"png"
    

}
generate_task = getimg.generate(text="beautiful woman",
make_output_public=True,
append_output_to_file=True,                                
options=options)

generate_task.wait()
output = generate_task.output    
print(output)
print(output.blocks[0])        