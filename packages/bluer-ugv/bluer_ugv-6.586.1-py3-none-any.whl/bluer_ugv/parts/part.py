from typing import List, Union
import copy

from bluer_objects import markdown


class Part:
    def __init__(
        self,
        info: Union[List[str], str] = [],
        name: str = "",
        images: List[str] = [],
    ):
        self.name = name

        self.info = (
            copy.deepcopy(info)
            if isinstance(
                info,
                list,
            )
            else [info]
        )

        self.images = (
            copy.deepcopy(images)
            if isinstance(
                images,
                list,
            )
            else [images]
        )

    @property
    def filename(self) -> str:
        return f"docs/parts/{self.name}.md"

    def image_url(
        self,
        url_prefix: str,
        filename: str = "",
    ) -> str:

        return (
            "{}/{}?raw=true".format(
                url_prefix,
                filename if filename else self.images[0],
            )
            if self.images
            else ""
        )

    def README(
        self,
        url_prefix: str,
    ) -> List[str]:
        return [f"- {info}" for info in self.info] + (
            [""]
            + markdown.generate_table(
                [
                    "![image]({})".format(
                        self.image_url(
                            url_prefix,
                            filename,
                        )
                    )
                    for filename in self.images
                ],
                cols=3,
            )
            if self.images
            else []
        )
