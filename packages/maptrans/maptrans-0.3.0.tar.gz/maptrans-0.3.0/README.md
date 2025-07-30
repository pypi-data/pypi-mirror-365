# Map Transform tool

copy idea from <https://epsg.io/>
but API from <https://www.maptiler.com/>

## Install

```sh
pip install maptrans
```

## Usage

make some data in csv like `sample.csv`

```csv
X,Y,H
20510210.743588,4058386.735392,155.55
20510196.183790,4057723.195846,123.45
```

transform by running command

```sh
mt --key <YOUR-KEY> --input sample.csv
```

> Get your FREE key from MapTiler

Default transform `CGCS2000 Zone 20` to `WGS 84`  
You can change the EPSG code

```sh
mt --key <YOUR-KEY> --input <INPUT-FILE> \
    --start <START-CODE> --to <TO-CODE>
```

- `START-CODE`: 4498 (CGCS2000 Zone 20) as default
- `TO-CODE`: 4326 (WGS 84) as default

get more details from <https://epsg.io/>
