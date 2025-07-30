from yta_video_moviepy.t import T, get_number_of_frames
from yta_general_utils.math.progression import Progression
from abc import ABC, abstractmethod


class ResizeAbsoluteChange(ABC):
    """
    Class that represent a variation of the video
    resized by absolute values. This resizing
    should be used directly to the video.
    """

    @property
    def number_of_frames(
        self
    ) -> int:
        """
        The number of frames affected by this
        change (which is the number of resize
        values we will have).
        """
        return get_number_of_frames(self.duration, self.fps)

    @property
    @abstractmethod
    def resizes(
        self
    ) -> list[int]:
        """
        The list of resize factors calculated for
        all the video frames.
        """
        pass

    def __init__(
        self,
        video_duration: float,
        video_fps: float,
    ):
        self.duration = video_duration
        """
        The duration of the video, to be able to
        calculate the values for the different frame
        time moments.
        """
        self.fps = video_fps
        """
        The frames per second of the video, to be 
        able to calculate the values for the different
        frame time moments.
        """

    def get_resize(
        self,
        t: float
    ) -> int:
        """
        Get the absolute resize factor for the
        provided 't' frame time moment. This
        resize factor must replace the current
        video resize factor.
        """
        return self.resizes[T.frame_time_to_frame_index(t, self.fps)]

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class ResizeAbsoluteDefault(ResizeAbsoluteChange):
    """
    The default value. This has to be used when
    we don't want to apply changes.
    """

    @property
    def resizes(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
        video frames.
        """
        if not hasattr(self, '_resizes'):
            self._resizes = [1.0] * self.number_of_frames

        return self._resizes

class ResizeAbsoluteTest(ResizeAbsoluteChange):
    """
    Just a test, I don't know...
    """

    @property
    def resizes(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
        video frames.
        """
        if not hasattr(self, '_resizes'):
            self._resizes = Progression(0.5, 1, self.number_of_frames).values

        return self._resizes