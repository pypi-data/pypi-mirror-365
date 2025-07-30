from enum import Enum
from typing import Dict, Optional


class WindowHop(Enum):
    """
    WindowHop represents the gap between consecutive audio windows.

    When WindowHop is smaller than WindowSize, audio windows overlap.
    The overlap makes inferences slower but reduces possibility of missing sounds between two different windows.

    For example, when WindowSize=1.0s and WindowHop=1.0s, audio windows are like below.
      - Window #0 (0.0s ~ 1.0s)
      - Window #1 (1.0s ~ 2.0s)
    If any important sound happened between the two windows (0.9s ~ 1.1s),
    it may not be detected because the sound is separated into two different windows.

    When WindowSize=1.0s and WindowHop=0.5s, audio windows are like below.
      - Window #0 (0.0s ~ 1.0s)
      - Window #1 (0.5s ~ 1.5s)
      - Window #2 (1.0s ~ 2.0s)
    Windows are overlapping, but less probability missing sound in between.
    """

    HOP_500ms = ('0.5s', 0.5)
    HOP_1s = ('1s', 1.0)

    def __init__(self, str_val: str, second_val: int):
        self.str_val: str = str_val
        self.second_val: int = second_val

    @property
    def str_value(self) -> str:
        """str: WindowHop Enum in string value."""
        return self.str_val

    @property
    def second(self) -> float:
        """float: WindowHop Enum in float second-unit value."""
        return self.second_val


class SensitivityScale(Enum):
    """
    SensitivityScale represents how sensitive a sound tag should be detected.
    High sensitivity means low threshold.
    It means that Cochl.Sense API determines a sound tag is detected even though its confidence is low.
    """

    VERY_HIGH = -2
    HIGH = -1
    MEDIUM = 0
    LOW = 1
    VERY_LOW = 2


class SensitivityConfig:
    """
    SensitivityConfig represents how sensitive each tag will be detected.

    Attributes:
        default (SensitivityScale): Default sensitivity applied to all tags not managed in `by_tags` attribute.
        by_tags (Dict[str, SensitivityScale]): Sensitivity of each tag. For example, {"Gunshot": SensitivityScale.LOW}
    """

    def __init__(self, default: SensitivityScale, by_tags: Optional[Dict[str, SensitivityScale]]):
        self.default: SensitivityScale = default
        self.by_tags: Optional[Dict[str, SensitivityScale]] = by_tags
        if self.by_tags is None:
            self.by_tags = {}


class ChunkSize(Enum):
    """
    ChunkSize represents how small a file is to be split when it is uploaded.
    A file is split into multiple chunks before it is uploaded to Cochl.Sense cloud.

    For example, when a 13MB file is uploaded with 5MB ChunkSize,
    two 5MB chunks and one 3MB chunk are uploaded to server.

    """

    SIZE_5MB = 5 * 10**6


class APIConfig:
    def __init__(
        self,
        # window_hop: WindowHop = WindowHop.HOP_500ms,
        chunk_size: ChunkSize = ChunkSize.SIZE_5MB,
        sensitivity: Optional[SensitivityConfig] = None,
        host: Optional[str] = None,
        # window_size: int = 1,
        speaker_recognition: bool = False,
        speaker_recognition_host: Optional[str] = None,
        custom_sound: bool = False,
        custom_sound_host: Optional[str] = None
    ):
        """
        Args:
            sensitivity: SensitivityConfig to apply in Cochl.Sense API Client.
        """
        # self.window_hop = window_hop
        self.chunk_size: ChunkSize = chunk_size
        self.sensitivity: Optional[SensitivityConfig] = sensitivity
        if self.sensitivity is None:
            self.sensitivity = SensitivityConfig(SensitivityScale.MEDIUM, {})

        self.host: Optional[str] = host
        # self.window_size = window_size
        # if self.window_size not in [1, 2]:
        #     raise ValueError(f"invalid window_size '{window_size}'")

        self.speaker_recognition: bool = speaker_recognition
        self.speaker_recognition_host: Optional[str] = speaker_recognition_host
        self.speaker_recognition_upload_max_file_count: int = 20
        self.speaker_recognition_upload_max_file_size: int = 10 * 1024 * 1024  # 10 MB

        self.custom_sound: bool = custom_sound
        self.custom_sound_host: Optional[str] = custom_sound_host

    def get_host(self) -> str:
        return 'https://api.cochl.ai/sense/api/v1' if self.host is None else self.host

    def get_speaker_recognition_host(self) -> str:
        if self.speaker_recognition_host is None:
            return 'https://sr-api.cochl.ai/api/v1'
        else:
            return self.speaker_recognition_host

    def get_custom_sound_host(self) -> str:
        return 'https://cs-api.cochl.ai/api/v1' if self.custom_sound_host is None else self.custom_sound_host
