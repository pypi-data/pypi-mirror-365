from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Literal, overload, override
from warnings import deprecated

import pyautogui as gui
import pyscreeze
from PIL import Image

from ._types import Direction, MouseButton
from .actions import locate_on_screen, move_and_click
from .box_array import BoxArray
from .shapes import Box, BoxSpec
from .utils import get_file


class ElementNotFoundError(Exception):
    """Exception raised when an element is not found on the screen."""

    pass


class ReferenceElement(ABC):
    """Base class for reference elements used to identify scenes."""

    name: str

    @overload
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "raise",
    ) -> BoxArray: ...
    @overload
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "raise",
    ) -> BoxArray | None: ...

    @abstractmethod
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "raise",
    ):
        """Detect the presence of the reference element."""
        raise NotImplementedError("Subclasses must implement this method")

    @deprecated("Use `locate().click()` instead.")
    def locate_and_click(
        self,
        region: BoxSpec | None = None,
        *,
        clicks: int = 1,
        button: MouseButton = "left",
        towards: Direction | None = None,
        offset: int = 0,
        index: int = 0,
    ):
        """Locate the reference element and click on it."""
        regions = self.locate(region=region, n=index + 1)
        assert regions is not None and len(regions) > index, (
            f"Element {self} not found on screen or insufficient detections {len(regions) if regions else 0} < {index + 1}."
        )
        if towards is not None:
            target_box = regions[index].offset(towards, offset)
        else:
            target_box = regions[index]
        move_and_click(target=target_box, clicks=clicks, button=button)


class ImageElement(ReferenceElement):
    """Reference element that identifies a scene by an image."""

    def __init__(
        self,
        path: str | list[str],
        confidence: float = 0.999,
        region: BoxSpec | None = None,
        locator: Callable[[Image.Image, Image.Image], BoxArray] | None = None,
    ):
        self.path = path
        self.confidence = confidence
        self.region = region
        self.locator = locator
        self.name = Path(path).stem if isinstance(path, str) else Path(path[0]).stem

    @overload
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "raise",
    ) -> BoxArray: ...
    @overload
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "raise",
    ) -> BoxArray | None: ...

    @override
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "raise",
    ):
        """Method to detect the presence of the image in the current screen."""
        if isinstance(self.path, str):
            path = [self.path]  # Ensure path is a list for consistency
        else:
            path = self.path

        all_locations: BoxArray = BoxArray()
        for image_path in path:
            try:
                locations = locate_on_screen(
                    image_path,
                    region=region if region else self.region,
                    confidence=self.confidence,
                    locator=self.locator,
                    limit=n - len(all_locations),  # Only get remaining needed locations
                )
                if locations is not None:
                    all_locations += locations

                # If we have enough detections, return them
                if len(all_locations) >= n:
                    return all_locations[:n]
            except (gui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
                continue

        if all_locations:
            return all_locations
        else:
            if error == "coerce":
                return None
            else:
                raise ElementNotFoundError(
                    f"{self} not found on screen in region {region}."
                )

    def __repr__(self) -> str:
        return f"ImageElement: {self.path}"


class ReferenceImageDir:
    def __init__(self, dir_path: Path | str) -> None:
        if isinstance(dir_path, str):
            dir_path = Path(dir_path)
        assert dir_path.is_dir(), f"{dir_path} is not a valid directory."
        self.dir_path = dir_path
        self.images: dict[str, ImageElement] = {}

    def __call__(
        self,
        image_name: str,
        region: BoxSpec | None = None,
        confidence: float = 0.999,
        locator: Callable[[Image.Image, Image.Image], BoxArray] | None = None,
    ) -> ImageElement:
        """Get an ImageElement from the reference directory."""
        if image_name not in self.images:
            image_path = get_file(self.dir_path, name=image_name)
            self.images[image_name] = ImageElement(
                str(image_path), region=region, confidence=confidence, locator=locator
            )
        return self.images[image_name]


def image(
    path: str,
    region: BoxSpec | None = None,
    confidence: float = 0.999,
    locator: Callable[[Image.Image, Image.Image], BoxArray] | None = None,
) -> ImageElement:
    """Create an image reference element."""
    return ImageElement(path, confidence=confidence, region=region, locator=locator)


class TextElement(ReferenceElement):
    """Reference element that identifies a scene by text."""

    def __init__(
        self,
        text: str,
        region: BoxSpec | None = None,
        case_sensitive: bool = False,
        full_text: bool = False,
    ):
        self.text = text
        self.region = region
        self.case_sensitive = case_sensitive
        self.full_text = full_text
        if not case_sensitive:
            self.text = self.text.lower()
        self.name = text

    @overload
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "raise",
    ) -> BoxArray: ...

    @overload
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "coerce",
    ) -> BoxArray | None: ...

    @override
    def locate(
        self,
        region: BoxSpec | None = None,
        n: int = 1,
        error: Literal["raise", "coerce"] = "raise",
    ):
        """Method to detect the presence of the text in the current screen."""
        from .ocr import OCR

        ocr = OCR()
        region = region or self.region
        found_regions = []

        for text, detected_region in ocr.recognize_text(
            gui.screenshot(region=Box.from_spec(region).to_tuple() if region else None)
        ):
            if not self.case_sensitive:
                text = text.lower()
            if self.full_text and text.strip() == self.text.strip():
                found_regions.append(detected_region.resolve(base=region))
            elif not self.full_text and self.text in text:
                found_regions.append(detected_region.resolve(base=region))
            # If we have enough detections, return them
            if len(found_regions) >= n:
                return BoxArray(found_regions[:n])

        if found_regions:
            return BoxArray(found_regions)
        else:
            if error == "coerce":
                return None
            else:
                raise ElementNotFoundError(
                    f"{self} not found on screen in region {region}."
                )

    def __repr__(self) -> str:
        return f"{{TextElement: {self.text}}}"


def text(
    text: str,
    region: BoxSpec | None = None,
    case_sensitive: bool = False,
    full_text: bool = False,
) -> TextElement:
    """Create a text reference element."""
    return TextElement(
        text=text, region=region, case_sensitive=case_sensitive, full_text=full_text
    )
