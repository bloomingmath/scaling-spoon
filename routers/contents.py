from typing import Callable, List, Optional

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import Response

from extensions.rendering import get_render
from extensions.signals import get_message_flashes
from models import User, Node, Group, Content
from extensions.mongo import mongo_engine
from pprint import pprint
from models import ObjectIdStr
import tempfile

router = APIRouter()


@router.get("/{content_id}")
async def read_content(content_id: ObjectIdStr, request: Request, flashes: list = Depends(get_message_flashes)):
    with tempfile.TemporaryFile() as file:
        content = Content.parse_obj((await mongo_engine.db["fs.files"].find_one({"_id": content_id}))["metadata"])
        await mongo_engine.fs.download_to_stream(content_id, file)
        pprint(content)
        file.seek(0)
        data = file.read()
    return Response(content=data, media_type=f"application/{content.filetype}")
