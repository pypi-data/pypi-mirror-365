import pytest

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.python.add_comments import add_comments

___generated_python_code = """

from magicgui import magicgui
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
import numpy as np
from typing import Union
from napari.types import ImageData
from magicgui import magicgui
import numpy as np
import cv2

@magicgui(call_button='Run')
def denoise_bilateral(image: ImageData, d: int = 15, sigmaColor: float = 75, sigmaSpace: float = 75) -> ImageData:
    img = image.astype(np.float32)
    img = cv2.bilateralFilter(img, d, sigmaColor, sigmaSpace)
    return img

"""


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_add_comments():
    # Add comments to the code:
    commented_code = add_comments(___generated_python_code)
    print(commented_code)

    # Check that the commented code is longer than the original code:
    assert len(commented_code) >= len(___generated_python_code)

    # Count the number of comments:
    assert commented_code.count("#") >= 2

    # Count the number of docstrings:
    assert commented_code.count('"""') >= 2
