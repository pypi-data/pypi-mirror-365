# cochl-sense-py

`cochl-sense-py` is a Python client library providing easy integration of Cochl.Sense API into any Python application. You can upload a file (MP3, WAV, OGG) or raw PCM audio stream. 

<br/>

## Installation

`cochl-sense-py` can be installed and used in Python 3.9+.

```python
pip install --upgrade cochl
```

<br/>

## Usage

This simple setup is enough to input your file. API project key can be retrieved from [Cochl Dashboard](https://dashboard.cochl.ai/).

```python
import cochl.sense as sense

client = sense.Client("YOUR_API_PROJECT_KEY")

results = client.predict("your_file.wav")
print(results.to_dict())  # get results as a dict
```

<br/>

You can adjust the custom settings like below. For more details please refer to [Advanced Cconfigurations](#advanced-configurations).
```python
import cochl.sense as sense

api_config = sense.APIConfig(
    sensitivity=sense.SensitivityConfig(
        default=sense.SensitivityScale.LOW,
        by_tags={
            "Baby_cry": sense.SensitivityScale.VERY_LOW,
            "Gunshot":  sense.SensitivityScale.HIGH,
        },
    ),
)

client = sense.Client(
    "YOUR_API_PROJECT_KEY",
    api_config=api_config,
)

results = client.predict("your_file.wav")
print(results.to_dict())  # get results as a dict
```

<br/>

The file prediction result can be displayed in a summarized format. More details at [Summarized Result](#summarzied-result).
```python
# print(results.to_dict())  # get results as a dict

print(results.to_summarized_result(
    interval_margin=2,
    by_tags={"Baby_cry": 5, "Gunshot": 3}
))  # get results in a simplified format

# At 0.0-1.0s, [Baby_cry] was detected
```

<br/>

Cochl.Sense API supports three file formats: MP3, WAV, OGG. \
If a file is not in a supported format, it has to be manually converted. More details [here](#convert-to-supported-file-formats-wav-mp3-ogg).


<br/>

## Advanced Configurations

### Sensitivity

Detection sensitivity can be adjusted for all tags or each tag individually. \
If you feel that tags are not detected well enough, increase sensitivities. If there are too many false detections, lower sensitivities.

The sensitivity is adjusted with `SensitivityScale` Enum.
  - `VERY_HIGH`
  - `HIGH`
  - `MEDIUM` (default)
  - `LOW`
  - `VERY_LOW`

```python
import cochl.sense as sense

api_config = sense.APIConfig(
    sensitivity=sense.SensitivityConfig(
        # default sensitivity applied to all tags not specified in `by_tags`
        default=sense.SensitivityScale.LOW,
        by_tags={
            "Baby_cry": sense.SensitivityScale.VERY_LOW,
            "Gunshot":  sense.SensitivityScale.HIGH,
        },
    ),
)
client = sense.Client(
    "YOUR_API_PROJECT_KEY",
    api_config=api_config,
)
```

<br/>
<br/>

## Other notes

### Convert to supported file formats (WAV, MP3, OGG)

`Pydub` is one of the easy ways to convert audio file into a supported format (WAV, MP3, OGG).

First install Pydub refering to this [link](https://github.com/jiaaro/pydub?tab=readme-ov-file#installation). \
Then write a Python script converting your file into a supported format like below.

```python
from pydub import AudioSegment

mp4_version = AudioSegment.from_file("sample.mp4", "mp4")
mp4_version.export("sample.mp3", format="mp3")
```

For more details of `Pydub`, please refer to this [link](https://github.com/jiaaro/pydub).

<br/>

### Summarzied Result
You can summarize the file prediction result by aggregating consecutive windows, returning the time and length of the detected tag. \
The 'interval margin' is a parameter that treats the unrecognized window between tags as part of the recognized ones and it affects all sound tags.
If you want to specify a different interval margin for specific sound tags, you can use the 'by_tags' option.

```python
print(results.to_summarized_result(
    interval_margin=2,
    by_tags={"Baby_cry": 5, "Gunshot": 3}
))

# At 0.0-1.0s, [Baby_cry] was detected
```

<br/>

### Links

Documentation: https://docs.cochl.ai/sense/api/
