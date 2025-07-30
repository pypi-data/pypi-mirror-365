"""
Module to wrap the functionality related to
basic video edition.
"""
from yta_video_editor.change.position import PositionChange
from yta_video_editor.change import _SetPosition, _SetRotation, _SetResize, _SetPositionValues, _SetRotationValues, _SetResizeValues
from yta_video_editor.utils import transform_video, put_video_over_black_background
from yta_video_moviepy.t import T
from yta_image_base.editor import ImageEditor
from yta_validation import PythonValidator
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator
from moviepy import VideoClip
from typing import Union
from yta_video_editor.settings import ZOOM_LIMIT, ROTATION_LIMIT, COLOR_TEMPERATURE_CHANGE_LIMIT, COLOR_HUE_CHANGE_LIMIT, BRIGHTNESS_LIMIT, CONTRAST_LIMIT, SHARPNESS_LIMIT, WHITE_BALANCE_LIMIT
from abc import ABC





class _UseTransformFactor(ABC):
    """
    Abstract class to represent the classes that
    will transform the video, frame by frame,
    using a factor that has to be validated.
    """

    def _validate_factor_type(
        self,
        factor: Union[int, list[int]]
    ):
        """
        Check if the 'factor' provided is a positive number or
        a list of positive numbers and raise an exception if
        not.
        """
        if (
            not NumberValidator.is_number(factor) and
            not PythonValidator.is_list_of_numbers(factor)
        ):
            raise Exception('The "factor" parameter provided is not a positive number nor a list of positive numbers.')
        
    def _validate_factor_value(
        self,
        number_of_frames: int,
        factor: Union[int, list[int]],
        limit: Union[tuple[int, int], None] = None
    ):
        """
        Check if the 'factor' value provided is valid
        according to the given 'limit' and the number
        of video frames.
        """
        if len(factor) != number_of_frames:
            raise Exception(f'The amount of "factor" elements ({str(len(factor))}) is not the same as the number of frames ({str(number_of_frames)}).')
        
        # TODO: Check that the 'limit' provided is valid (?)
        if limit is not None:
            for f in factor:
                ParameterValidator.validate_mandatory_number_between('factor', f, limit[0], limit[1])

    def validate_and_process_transform_factor(
        self,
        number_of_frames: int,
        factor: Union[int, list[int]],
        limit: Union[tuple[int, int], None] = None
    ) -> Union[int, list[int]]:
        """
        Validate the provided 'factor', raising an
        exception if invalid, and process it to 
        return an array of factor values with
        'number_of_frames' elements.
        """
        self._validate_factor_type(factor)
    
        factor = (
            [factor] * number_of_frames
            if not PythonValidator.is_list(factor) else
            factor
        )

        self._validate_factor_value(number_of_frames, factor, limit)

        return factor

class _Color(_UseTransformFactor):
    """
    Class to handle the color variations of a
    video when inside a VideoEditor instance.
    """

    def __init__(
        self,
        editor: 'VideoEditor'
    ):
        self.editor: VideoEditor = editor
        """
        The VideoEditor instance this _Color instance
        belongs to.
        """

    def temperature(
        self,
        factor: Union[int, list[int]] = 0
    ) -> 'VideoEditor':
        """
        Set the color temperature of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`
        """
        return self._apply_color_transform(
            factor,
            COLOR_TEMPERATURE_CHANGE_LIMIT,
            lambda editor, frame: editor.color.temperature(frame).image
        )
    
    def hue(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color hue of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`
        """
        return self._apply_color_transform(
            factor,
            COLOR_HUE_CHANGE_LIMIT,
            lambda editor, frame: editor.color.hue(frame).image
        )
    
    def brightness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color brightness of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        return self._apply_color_transform(
            factor,
            BRIGHTNESS_LIMIT,
            lambda editor, frame: editor.color.brightness(frame).image
        )
    
    def contrast(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color contrast of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        return self._apply_color_transform(
            factor,
            CONTRAST_LIMIT,
            lambda editor, frame: editor.color.contrast(frame).image
        )

    def sharpness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color sharpness of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        return self._apply_color_transform(
            factor,
            SHARPNESS_LIMIT,
            lambda editor, frame: editor.color.sharpness(frame).image
        )

    def white_balance(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color white balance of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        return self._apply_color_transform(
            factor,
            WHITE_BALANCE_LIMIT,
            lambda editor, frame: editor.color.white_balance(frame).image
        )
    
    def _apply_color_transform(
        self,
        factor: float,
        limit: tuple[int, int],
        transform_fn: callable
    ):
        factor = self.validate_and_process_transform_factor(
            self.editor._video.n_frames,
            factor,
            limit
        )

        def _wrapper(frame, factor):
            return transform_fn(ImageEditor(frame), factor)

        self.editor._video = transform_video(
            video = self.editor._video,
            factor = factor,
            transform_fn = _wrapper,
        )

        return self.editor

# TODO: This single editor is used in the
# image library as a simple editor that is
# called from the image class instance...
# so maybe this should be very simple. It
# is also in the 'yta_image_base' library 
# and not in a different one
class VideoEditor:
    """
    Class to simplify and encapsulate all the
    functionality related to video edition.

    This VideoEditor works editing the video
    that has been providing when instantiating
    this class. All the changes you make will
    be chained.

    # TODO: I read that an interesting thing 
    is to store the operations you want to do
    in a list, and to perform all of them when
    needed. You can also revert the steps in
    that way. How can we do that? Also, if we
    want to apply zoom and then apply zoom
    again, that shouldn't be possible. We can
    add one zoom attribute that is the one we
    will apply, but not zoom x zoom.
    """

    @property
    def video(
        self
    ) -> VideoClip:
        """
        The moviepy video we are editing, with
        all the changes applied.
        """
        return self._video
    
    @property
    def copy(
        self
    ) -> VideoClip:
        """
        A copy of the video we are editing, with
        all the changes applied.
        """
        return self.video.copy()

    @property
    def color(
        self
    ):
        """
        The properties related to color we can change.
        """
        return self._color

    def __init__(
        self,
        video: VideoClip
    ):
        ParameterValidator.validate_mandatory_instance_of('video', video, VideoClip)

        self._original_video = video
        """
        The original video as it was loaded with
        no changes on it.
        """
        self._video = self._original_video.copy()
        """
        The moviepy video we are editing, with
        all the changes applied.
        """
        self._color: _Color = _Color(self)

    def zoom(
        self,
        factor: int = 100
    ) -> 'VideoEditor':
        """
        Apply zoom on the video. A factor of 1 means x0.01 zoom,
        which is a zoom out. A factor of 200 means x2.00 zoom,
        which is a zoom in.
        """
        ParameterValidator.validate_mandatory_number_between('factor', factor, ZOOM_LIMIT[0], ZOOM_LIMIT[1])

        factor = int(factor)

        new_size = (
            factor / 100 * self.video.size[0],
            factor / 100 * self.video.size[1]
        )

        self._video = put_video_over_black_background(self.video.resized(new_size))

        return self
    
    def move(
        self,
        x_variation: int = 0,
        y_variation: int = 0
    ) -> 'VideoEditor':
        """
        Apply a movement in the video, which means that it
        will be not centered if 'x_variation' and/or
        'y_variation' are different from zero.

        TODO: I don't like the 'move' method name
        """
        # TODO: Any limit must be set in a general VideoEditor
        # settings file
        X_LIMIT = (-1920, 1920)
        Y_LIMIT = (-1080, 1080)

        ParameterValidator.validate_mandatory_number_between('x_variation', x_variation, X_LIMIT[0], X_LIMIT[1])
        ParameterValidator.validate_mandatory_number_between('y_variation', y_variation, Y_LIMIT[0], Y_LIMIT[1])

        x_variation = int(x_variation)
        y_variation = int(y_variation)

        self._video = put_video_over_black_background(self.video, position = (x_variation, y_variation))

        return self
    
    def rotate(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Apply a rotation in the video. A positive rotation
        will rotate it clockwise, and a negative one,
        anti-clockwise. A factor of 90 means rotating it 90
        degrees to the right (clockwise).
        """
        ParameterValidator.validate_mandatory_number_between('factor', factor, ROTATION_LIMIT[0], ROTATION_LIMIT[1])

        factor = int(factor % 360)

        self._video = put_video_over_black_background(self.video.rotated(factor))

        return self
    
    # TODO: Maybe these ones below could be with
    # the dynamic attribute format (single value,
    # array, etc.)
    def set_color_temperature(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color temperature of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`

        This is a shortcut of:
        - `VideoEditor(video).color.temperature(factor)`.
        """
        return self.color.temperature(factor)

    def set_color_hue(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color hue of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`

        This is a shortcut of:
        - `VideoEditor(video).color.hue(factor)`.
        """
        return self.color.hue(factor)
    
    def set_color_brightness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color brightness of the image.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.brightness(factor)`.
        """
        return self.color.brightness(factor)

    def set_color_contrast(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color contrast of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.contrast(factor)`.
        """
        return self.color.contrast(factor)

    def set_color_sharpness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color sharpness of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.sharpness(factor)`.
        """
        return self.color.sharpness(factor)

    def set_color_white_balance(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color white_balance of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.white_balance(factor)`.
        """
        return self.color.white_balance(factor)
    
    # TODO: All inside this method has to be refactored
    # and moved, but I managed to make it work!
    def process_test(
        self,
        filename: str,
        do_quick: bool = True
    ) -> str:
        # TODO: Test processing the movements, rotation, etc
        # by different effects.

        # Subclip to test quick
        self._video = (
            self.video.with_subclip(0, 0.5)
            if do_quick else
            self.video
        )

        # Precalculate the 'ts' for all the changes
        from yta_video_editor.change import Changes
        from yta_video_editor.change.position.absolute import PositionAbsoluteFromAtoB
        from yta_video_editor.change.rotation.absolute import RotationAbsoluteSpinXTimes
        from yta_video_editor.change.resize.absolute import ResizeAbsoluteTest

        changes = Changes()
        changes.add(PositionAbsoluteFromAtoB(self.video.duration, self.video.fps, (-100, -100), (400, 400)))
        changes.add(RotationAbsoluteSpinXTimes(self.video.duration, self.video.fps, 2))
        changes.add(ResizeAbsoluteTest(self.video.duration, self.video.fps))

        self._video = changes.apply(self.video)

        # TODO: Check this:
        # If I set the position but I don't use a 
        # black background, the position is set but
        # the scene doesn't change because there is
        # only one single video, so I think using
        # this black background should be just the
        # last step for the final compound sum of
        # video layers just in case, but not here
        self.save_as(filename)

        return filename

    def save_as(
        self,
        filename: str
    ) -> str:
        """
        Save the video with all the modifications to
        the provided 'filename'.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        self.video.write_videofile(filename)

        return filename

