from yta_video_moviepy.t import T, get_number_of_frames
from abc import ABC, abstractmethod


class RotationAbsoluteChange(ABC):
    """
    Class that represent a variation of the video
    rotation by absolute values. This rotation
    should be used directly to the video.
    """

    @property
    @abstractmethod
    def rotations(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
        video frames.
        """
        pass

    def __init__(
        self,
        # TODO: Maybe 'number_of_frames' instead of
        # 'duration' (?)
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

    def get_rotation(
        self,
        t: float
    ) -> int:
        """
        Get the absolute rotation for the provided 't'
        frame time moment. This rotation must replace
        the current video rotation.
        """
        return self.rotations[T.frame_time_to_frame_index(t, self.fps)]

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class RotationAbsoluteDefault(RotationAbsoluteChange):
    """
    The default value. This has to be used when
    we don't want to apply changes.
    """

    @property
    def rotations(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
        video frames.
        """
        if not hasattr(self, '_rotations'):
            self._rotations = [0] * get_number_of_frames(self.duration, self.fps)

        return self._rotations

class RotationAbsoluteSpinXTimes(RotationAbsoluteChange):
    """
    Spin the video X times.
    """

    @property
    def rotations(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
        video frames.
        """
        if not hasattr(self, '_rotations'):
            # TODO: Calculate properly
            # This is just a shitty example to be able
            # to check the classes structure and
            # behaviour
            number_of_frames = get_number_of_frames(self.duration, self.fps)
            self._rotations = [
                ((frame_index / number_of_frames) * 360 * self.times) % 360
                for frame_index in range(number_of_frames)
            ]

        return self._rotations

    def __init__(
        self,
        # TODO: Maybe 'number_of_frames' instead of
        # 'duration' (?)
        video_duration: float,
        video_fps: float,
        times: int = 1
    ):
        super().__init__(video_duration, video_fps)

        # TODO: Validate times
        self.times = times