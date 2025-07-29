import asyncio
from datetime import datetime
from typing import ClassVar, Literal

from oibot.api.send_message import (
    Ark,
    Keyboard,
    Markdown,
    SendMessageResponse,
    send_message,
)
from oibot.event import Context, Event


class GroupAtMessageCreateEvent(Event):
    __slots__ = (
        "__weakref__",
        "id",
        "content",
        "timestamp",
        "author",
        "attachments",
        "group_id",
        "group_openid",
        "message_scene",
        "message_type",
    )

    class Author:
        __slots__ = ("id", "member_openid", "union_openid")

        def __init__(self, *, id: str, member_openid: str, union_openid: str) -> None:
            self.id = id
            self.member_openid = member_openid
            self.union_openid = union_openid

        def __repr__(self) -> str:
            return f"""{self.__class__.__name__}({
                ", ".join(
                    f"{item}={value}"
                    for item in self.__slots__
                    if (not item.startswith("__"))
                    and (value := getattr(self, item, None))
                )
            })"""

    class Attachment:
        __slots__ = ("content_type", "filename", "height", "size", "url", "width")

        def __init__(
            self,
            *,
            content_type: str,
            filename: str,
            height: int,
            size: int,
            url: str,
            width: int,
        ) -> None:
            self.content_type = content_type
            self.filename = filename
            self.height = height
            self.size = size
            self.url = url
            self.width = width

        def __repr__(self) -> str:
            return f"""{self.__class__.__name__}({
                ", ".join(
                    f"{item}={value}"
                    for item in self.__slots__
                    if (not item.startswith("__"))
                    and (value := getattr(self, item, None))
                )
            })"""

    class MessageScene:
        __slots__ = "source"

        def __init__(self, *, source: str) -> None:
            self.source = source

        def __repr__(self) -> str:
            return f"""{self.__class__.__name__}({
                ", ".join(
                    f"{item}={value}"
                    for item in self.__slots__
                    if (not item.startswith("__"))
                    and (value := getattr(self, item, None))
                )
            })"""

    event_type: ClassVar[Literal["GROUP_AT_MESSAGE_CREATE"]] = "GROUP_AT_MESSAGE_CREATE"

    id: str
    content: str
    timestamp: datetime
    author: Author
    attachments: list[Attachment]
    group_id: str
    group_openid: str

    message_scene: MessageScene
    message_type: int

    futures: ClassVar[dict[tuple[str, str], asyncio.Future]] = {}

    def __init__(self, *, ctx: Context) -> None:
        d = ctx["d"]

        author = d["author"]
        message_scene = d["message_scene"]

        self.id = d["id"]
        self.content = d["content"]
        self.timestamp = datetime.fromisoformat(d["timestamp"])
        self.author = self.Author(
            id=author["id"],
            member_openid=author["member_openid"],
            union_openid=author["union_openid"],
        )

        self.attachments = (
            [
                self.Attachment(
                    content_type=attachment["content_type"],
                    filename=attachment["filename"],
                    height=attachment["height"],
                    size=attachment["size"],
                    url=attachment["url"],
                    width=attachment["width"],
                )
                for attachment in attachments
            ]
            if (attachments := d.get("attachments"))
            else []
        )

        self.group_id = d["group_id"]
        self.group_openid = d["group_openid"]
        self.message_scene = self.MessageScene(source=message_scene["source"])
        self.message_type = d["message_type"]

        super().__init__(ctx=ctx)

        if future := self.__class__.futures.get(
            (self.group_openid, self.author.member_openid)
        ):
            future.set_result(self)

    async def reply(
        self,
        content: str | None = None,
        *,
        markdown: Markdown | None = None,
        keyboard: Keyboard | None = None,
        ark: Ark | None = None,
        image: bytes | str | None = None,
        video: bytes | str | None = None,
        voice: bytes | str | None = None,
    ) -> SendMessageResponse:
        return await send_message(
            group_openid=self.group_openid,
            content=content,
            markdown=markdown,
            keyboard=keyboard,
            ark=ark,
            image=image,
            video=video,
            voice=voice,
            msg_id=self.id,
        )

    async def defer(
        self,
        content: str | None = None,
        *,
        markdown: Markdown | None = None,
        keyboard: Keyboard | None = None,
        ark: Ark | None = None,
        image: bytes | str | None = None,
        video: bytes | str | None = None,
        voice: bytes | str | None = None,
    ) -> tuple["GroupAtMessageCreateEvent", SendMessageResponse]:
        self.__class__.futures[(self.group_openid, self.author.member_openid)] = (
            future
        ) = asyncio.get_running_loop().create_future()

        defer_message_response = await send_message(
            group_openid=self.group_openid,
            content=content,
            markdown=markdown,
            keyboard=keyboard,
            ark=ark,
            image=image,
            video=video,
            voice=voice,
            msg_id=self.id,
        )

        try:
            return await future, defer_message_response

        finally:
            del self.__class__.futures[(self.group_openid, self.author.member_openid)]
