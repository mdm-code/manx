A toolkit for early Middle English lemmatization based on data from
[eLALME](http://www.lel.ed.ac.uk/ihd/laeme2/laeme2.html). This project, a proof
of concept so to speak, exists for research and educational purposes only. It
shows how corpus data from historical languages can be used to fine-tune large
language models to support researchers in their daily work. The project does
not infringe upon the copyright statement for eLAEME given [here](). Data is
not distributed; it is transformed in order to make use of it for the purpose
of the project. The project is distributed under the GPL-3 license meaning all
its research and all other derivatives (most notably) of whatever kind are to
be distributed under the same GPL-3 license and made publicly available in
full. Whenever the project is used make sure to explicitly
reference this repository and the original eLAEME corpus.


## Installation

In order to use `manx` on your machine, you have to install it first using
Python. You can install it from this repository with the following command:

```sh
python3 -m pip install manx@git+https://github.com/mdm-code/manx.git
```

I am not a big fan of cluttering the Python package index with all sorts of
code that folks come up with, and I decided to stick with a simple repository.

As for the version of Python, use Python `>=3.10` as declared in the
`pyproject.toml` file.

Once installed, you should be able to invoke `manx -h` from your terminal.


## Usage

Now, when it comes to how you can use `manx` to fiddle with the data from
eLAEME, fine-tune a T5 model yourself, etc., you can key in `manx -h` to
see all the available options. There three commands that `manx` supports:

- download: lets you download corpus files and store them on disk
- parse: parse the corpus, for instance, for model fine tuning
- api: serve the fine-tuned model behind a REST API

While `download` is pretty much straightforward: you give it a `-r` root, then
files are pulled from the website and stored on the drive, the other two
commands could use a more detailed description. The command `parse` lets you
parse the corpus from the files you pulled with `download` or parse them
directly `from the web` using `--from-web` flag. You can specify the length of
parsed ngrams extracted from the corpus or the size of document chunks later
used to shuffle the corpus parts. The two options are useful when `--fromat` is
set to `t5`. The default command to get data from eLAEME for model fine-tuning
would look like this:

```sh
manx parse \
	--verbose \
	--from-web \
	--format t5 \
	--ngram-size 11 \
	--chunk-size 200 \
	--t5prefix Lemmatize \
	--output t5-laeme-data.csv
```

You can `head t5-laeme-data.csv` to get the idea of how the resulting CSV file
looks like.

As for the `api` command, it lets you specify the host and the port to serve the
API. Other environmental variables that can be specified in the `.env` file
or exported in the local environment are given below, so feel free to tweak them
to you liking.

```sh
MANX_API_HOST=localhost
MANX_API_PORT=8000
MANX_API_LOG_LEVEL=INFO
MANX_API_TEXT_PLACEHOLDER=YOUR PLACEHOLDER TEXT
MANX_MODEL_TYPE=byt5
MANX_MODEL_DIR=mdm-code/me-lemmatize-byt5-small
MANX_USE_GPU=False
```

You can serve the API locally with default parameters like so: `manx api`. The
default model served on Huggingface used under the hood will be pulled the
moment the `/v1/lemmatize` API endpoint is called for the first time. You can
change the path through environmental variables to point to your own models
sorted locally or hosted on Huggingface.


## Development

You want to have the package pulled the usual way with `git` and then installed
for development purposes with `python3 -m pip install -e .`. To run tests,
linters and type checkers, use `make test`. Have a look at the `Makefile` and
`.github/workflows` to see what is already available and what is expected.


## License

Copyright (c) 2023 Michał Adamczyk.

This project is licensed under the [GPL-3 license](https://opensource.org/licenses/gpl-3-0).
See [LICENSE](LICENSE) for more details.
