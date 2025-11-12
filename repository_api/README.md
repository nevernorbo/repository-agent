# Code search with Qdrant using tree-sitter

This fork is a slightly different implementation of the [original](https://github.com/qdrant/demo-code-search) project. The major difference being the use of tree-sitter to parse code written in multiple different languages with ease.

## Prerequisites

- **Read the readme of [qdrant/demo-code-search](https://github.com/qdrant/demo-code-search)**
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Description

For indexing this project similarly uses:
- `all-MiniLM-L6-v2` - one of the gold standard models for natural language processing
- `microsoft/unixcoder-base` - a model trained specifically on a code dataset

Out of the box, the project supports four languages:
- Python,
- JavaScript
- TypeScript
- C#

But this can be easily extended. See the "Adding support for more languages" section of this README.

## Usage

### Data indexing

Qdrant is used as a search engine, so you will need to have it running somewhere. You can either use the local container
or the Cloud version. If you want to use the local version, you can start it with the following command:

```shell
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

However, the easiest way to start using Qdrant is to use our Cloud version. You can sign up for a free tier 1GB cluster 
at [https://cloud.qdrant.io/](https://cloud.qdrant.io/).

Set up the environment:
```shell
# From the root directory
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```
Once the environment is set up, you can configure the Qdrant instance and build the index by running the following commands:

```shell
export QDRANT_URL="http://localhost:6333"

# For the Cloud service you need to specify the api key as well
# export QDRANT_API_KEY="your-api-key"

# Before running this make sure to look at this file and set a repository first!
bash tools/download_and_index.sh
```

The indexing process might take a while, as it needs to encode all the code snippets and send them to the Qdrant.

### Search service

Once the index is built, you can start the search service by running the following commands:

```shell
docker-compose up
```

The UI will be available at [http://localhost:8000/](http://localhost:8000/). This is how it should look like:

![Code search with Qdrant](images/code-search-ui.png)

You can type in the search query and see the related code structures. Queries might come both from natural language
but also from the code itself. 

## Adding support for more languages

1. Open `./code_search/index/language_definitions.py` and add the programming languages you'd like ([view supported languages](https://github.com/Goldziher/tree-sitter-language-pack))
2. In this same file, don't forget to add a new key value pair to the extensions as well!
3. Now go to `./code_search/index/parser_common.py` and read through the code and docstrings, based on this you should now see what you'll need to implement for the newly added language.
4. Look through the docs of tree-sitter-[*new language*] (e.g [tree-sitter-rust](https://github.com/tree-sitter/tree-sitter-rust)) and figure out what data you need.
5. Done!
