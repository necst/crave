# crAVe

crAVe can test and explore the capabilities of the AV engines included in VirutTotal.

## Install

`pip install -r requirements.txt`

## Config

`default.json`:

```
{
    "VT_API_KEY": "",
    "no_submit": false,
    "tests": ["emu"],
    "samples": {
        "goodware": {
            "sample": "base_samples/helloword.exe",
            "dropper": "base_samples/droppergoodware.exe",
            "packed": {
                "UPX": "base_samples/helloword_upx.exe",
                "MEW": "base_samples/helloword_mew.exe"
            }
        },
        "malware": {
            "sample": "base_samples/virut.exe",
            "dropper": "base_samples/virut_dropper.exe",
            "packed": {
                "UPX": "base_samples/virut_upx.exe",
                "MEW": "base_samples/virut_mew.exe"
            }
        }
    }
}

```

## Run

`python crave.py <CONFIG_FILE> <OUTPUT_DIR>`
