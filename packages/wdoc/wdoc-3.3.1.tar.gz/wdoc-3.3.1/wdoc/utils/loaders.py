"""
Called by batch_file_loader.py's threads. Contains many cached function to
load each document.
"""

import copy
import inspect
import json
import os
import re
import shutil
import signal
import sys
import tempfile
import time
import traceback
import warnings
from contextlib import contextmanager
from functools import cache as memoize
from functools import partial, wraps
from pathlib import Path

import joblib

import ankipandas as akp
import bs4
import deepgram
import dill
import ffmpeg
import ftfy
import goose3
import httpx
import litellm
import LogseqMarkdownParser
import openparse
import pandas as pd
import playwright.sync_api
import pydub
import requests
import uuid6
import yt_dlp as youtube_dl
from beartype.typing import Any, Callable, Dict, List, Optional, Tuple, Union, Literal
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from langchain_community.document_loaders import (
    Docx2txtLoader,
    OnlinePDFLoader,
    PDFMinerLoader,
    PDFPlumberLoader,
    PlaywrightURLLoader,
    PyMuPDFLoader,
    PyPDFium2Loader,
    PyPDFLoader,
    SeleniumURLLoader,
    UnstructuredEPubLoader,
    UnstructuredPDFLoader,
    UnstructuredPowerPointLoader,
    UnstructuredURLLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
)
from prompt_toolkit import prompt
from tqdm import tqdm
from unstructured.cleaners.core import clean_extra_whitespace
from loguru import logger

from wdoc.utils.env import env, is_linux, is_out_piped
from wdoc.utils.errors import TimeoutPdfLoaderError, MissingDocdictArguments
from wdoc.utils.misc import (
    ModelName,
    average_word_length,
    check_docs_tkn_length,
    doc_loaders_cache,
    file_hasher,
    get_splitter,
    hasher,
    html_to_text,
    is_timecode,
    max_token,
    min_lang_prob,
    min_token,
    optional_strip_unexp_args,
    seconds_to_timecode,
    timecode_to_second,
    wpm,
)

try:
    import torchaudio
except Exception as e:
    # torchaudio can be tricky to install to just in case let's avoid crashing wdoc entirely
    logger.warning(f"Failed to import torchaudio: '{e}'")

try:
    import pdftotext
except Exception as err:
    if env.WDOC_VERBOSE:
        logger.warning(f"Failed to import optional package 'pdftotext': '{err}'")
        if is_linux:
            logger.warning(
                "On linux, you can try to install pdftotext with :\nsudo "
                "apt install build-essential libpoppler-cpp-dev pkg-config "
                "python3-dev\nThen:\nuv pip install pdftotext"
            )

# needed in case of buggy unstructured install
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

STR_IMAGE_OCR = "{image_ocr_alt}"

# Mapping of filetypes to their corresponding loader function names
FILETYPE_TO_LOADER = {
    "url": "load_url",
    "youtube": "load_youtube_video",
    "pdf": "load_pdf",
    "online_pdf": "load_online_pdf",
    "anki": "load_anki",
    "string": "load_string",
    "txt": "load_txt",
    "text": "load_text_input",
    "local_html": "load_local_html",
    "logseq_markdown": "load_logseq_markdown",
    "local_audio": "load_local_audio",
    "local_video": "load_local_video",
    "online_media": "load_online_media",
    "epub": "load_epub",
    "powerpoint": "load_powerpoint",
    "word": "load_word_document",
    "json_dict": "load_json_dict",
}

clozeregex = re.compile(r"{{c\d+::|}}")  # for removing clozes in anki
markdownlink_regex = re.compile(r"\[.*?\]\((.*?)\)")  # to find markdown links
# to replace markdown links by their text
markdownlinkparser_regex = re.compile(r"\[([^\]]+)\]\(http[s]?://[^)]+\)")
# to remove image from jina reader that take a lot of tokens but are not yet used
markdownimage_regex = re.compile(
    r"!\[([^\]]*)\]\s*(\([^\)]+\)|\[[^\]]+\])", flags=re.MULTILINE
)


def md_shorten_image_name(md_image: re.Match) -> str:
    "turn a markdown image link into just the name"
    name = md_image.group(1)
    if len(name) <= 16:
        return name
    else:
        return name[:8] + "…" + name[-8:]


# to check that a youtube link is valid
yt_link_regex = re.compile("youtube.*watch")
emptyline_regex = re.compile(r"^\s*$", re.MULTILINE)
emptyline2_regex = re.compile(r"\n\n+", re.MULTILINE)
linebreak_before_letter = re.compile(
    r"\n([a-záéíóúü])", re.MULTILINE
)  # match any linebreak that is followed by a lowercase letter
anki_replacements_regex = re.compile(r"\{([^}]*)\}")


class OpenparseDocumentParser:
    def __init__(
        self,
        path: Union[str, Path],
        table_args: Optional[dict] = {
            "parsing_algorithm": "pymupdf",
            "table_output_format": "markdown",
        },
        # table_args: Optional[dict] = None,
    ) -> None:
        self.path = path
        self.table_args = table_args

    def load(self) -> List[Document]:
        parser = openparse.DocumentParser(table_args=self.table_args)
        self.parsed = parser.parse(self.path)

        base_metadata = self.parsed.dict()
        nodes = base_metadata["nodes"]
        assert nodes, "No nodes found"
        del base_metadata["nodes"]

        docs = []
        for node in nodes:
            meta = base_metadata.copy()
            meta.update(node)
            assert meta["bbox"], "No bbox found"
            meta["page"] = meta["bbox"][0]["page"]
            text = meta["text"]
            del meta["text"], meta["bbox"], meta["node_id"], meta["tokens"]
            if meta["embedding"] is None:
                del meta["embedding"]

            doc = Document(
                page_content=text,
                metadata=meta,
            )

            if not docs:
                docs.append(doc)
            elif docs[-1].metadata["page"] != meta["page"]:
                docs.append(doc)
            else:
                docs[-1].page_content += "\n" + doc.page_content
                for k, v in doc.metadata.items():
                    if k not in docs[-1].metadata:
                        docs[-1].metadata[k] = v
                    else:
                        val = docs[-1].metadata[k]
                        if v == val:
                            continue
                        elif isinstance(val, list):
                            if v not in val:
                                if isinstance(v, list):
                                    docs[-1].metadata[k].extend(v)
                                else:
                                    docs[-1].metadata[k].append(v)
                        else:
                            docs[-1].metadata[k] = [val, v]
        self.docs = docs
        return docs


pdf_loaders = {
    "pymupdf": PyMuPDFLoader,  # good for metadata
    "pdfplumber": PDFPlumberLoader,  # good for metadata
    "pdfminer": PDFMinerLoader,  # little metadata
    "pypdfloader": PyPDFLoader,  # little metadata
    "pypdfium2": PyPDFium2Loader,  # little metadata
    # "pdftotext": None,  # optional support, see below
    "openparse": OpenparseDocumentParser,  # gets page number too, finds individual elements, kinda slow but good, optional table support
    "unstructured_fast": partial(
        UnstructuredPDFLoader,
        strategy="fast",
    ),
    "unstructured_elements_fast": partial(
        UnstructuredPDFLoader,
        mode="elements",
        strategy="fast",
    ),
    "unstructured_hires": partial(
        UnstructuredPDFLoader,
        strategy="hi_res",
    ),
    "unstructured_elements_hires": partial(
        UnstructuredPDFLoader,
        mode="elements",
        strategy="hi_res",
    ),
    "unstructured_fast_clean_table": partial(
        UnstructuredPDFLoader,
        strategy="fast",
        post_processors=[clean_extra_whitespace],
        infer_table_structure=True,
        # languages=["en"],
    ),
    "unstructured_elements_fast_clean_table": partial(
        UnstructuredPDFLoader,
        mode="elements",
        strategy="fast",
        post_processors=[clean_extra_whitespace],
        infer_table_structure=True,
        # languages=["en"],
    ),
    "unstructured_hires_clean_table": partial(
        UnstructuredPDFLoader,
        strategy="hi_res",
        post_processors=[clean_extra_whitespace],
        infer_table_structure=True,
        # languages=["en"],
    ),
    "unstructured_elements_hires_clean_table": partial(
        UnstructuredPDFLoader,
        mode="elements",
        strategy="hi_res",
        post_processors=[clean_extra_whitespace],
        infer_table_structure=True,
        # languages=["en"],
    ),
}

# pdftotext is kinda weird to install on windows so support it
# only if it's correctly imported
if "pdftotext" in sys.modules:

    class pdftotext_loader_class:
        "simple wrapper for pdftotext to make it load by pdf_loader"

        def __init__(self, path: Union[str, Path]) -> None:
            self.path = path

        def load(self) -> List[Document]:
            with open(self.path, "rb") as f:
                docs = [
                    Document(page_content=d, metadata={"page": idoc})
                    for idoc, d in enumerate(pdftotext.PDF(f))
                ]
                return docs

    pdf_loaders["pdftotext"] = pdftotext_loader_class

# unsilence audio
sox_effects = [
    ["norm"],  # normalize audio
    # isolate voice frequency
    # human speech for low male is about 100hz and high female about 17khz
    ["highpass", "-1", "100"],
    ["lowpass", "-1", "17000"],
    # -2 is for a steeper filtering: removes high frequency and very low ones
    ["highpass", "-2", "50"],
    ["lowpass", "-2", "18000"],
    ["norm"],  # normalize audio
    # max silence should be 3s
    ["silence", "-l", "1", "0", "1%", "-1", "3.0", "1%"],
    ["norm"],
]


def debug_return_empty(func: Callable) -> Callable:
    if env.WDOC_EMPTY_LOADER:

        @wraps(func)
        def wrapper(*args, **kwargs):
            metadata = {
                "debug_empty": True,
                "content_hash": str(uuid6.uuid6()),
                "all_hash": str(uuid6.uuid6()),
            }
            metadata.update(kwargs)
            out = [
                Document(
                    page_content="Lorem Ipsum",
                    metadata=metadata,
                )
            ]
            return out

        return wrapper
    else:
        return func


pdf_loader_max_timeout = env.WDOC_MAX_PDF_LOADER_TIMEOUT
if env.WDOC_VERBOSE:
    if pdf_loader_max_timeout > 0:
        logger.warning(f"Will use a PDF loader timeout of {pdf_loader_max_timeout}s")
    else:
        logger.warning("Not using a pdf loader timeout")


@contextmanager
def signal_timeout(timeout: int, exception: Exception):
    "disabled in some joblib backend"
    assert timeout > 0, f"Invalid timeout: {timeout}"

    def signal_handler(signum, frame):
        raise exception("Timeout occurred")

    # Set the signal handler and an alarm
    disabled = False
    try:
        signal.signal(signal.SIGALRM, signal_handler)
    except Exception:
        disabled = True

    if disabled:
        yield
    else:
        signal.alarm(timeout)

        try:
            yield
        finally:
            # Disable the alarm
            signal.alarm(0)


def wrapper_load_one_doc(func: Callable) -> Callable:
    """Decorator to wrap doc_loader to catch errors cleanly"""

    # # load_one_doc wrapped can also return a str, the error message,
    # # wraps(func) removes it so we readd it:
    newfunc = copy.copy(func)
    newfunc.__annotations__["return"] = Union[List[Document], str]

    @wraps(newfunc)
    def wrapper(*args, **kwargs) -> Union[List[Document], str]:
        # Extract loading_failure from kwargs, default to "warn"
        loading_failure = kwargs.pop("loading_failure", "warn")

        try:
            return func(*args, **kwargs)
        except Exception as err:

            # those crashes can rise right away without more details
            if loading_failure == "crash":
                if isinstance(err, (MissingDocdictArguments, TimeoutPdfLoaderError)):
                    raise

            filetype = kwargs.get("filetype", "unknown")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            formatted_tb = "\n".join(traceback.format_tb(exc_tb))
            if "pdf parser" in str(err).lower() and "to parse" in str(err).lower():
                mess = (
                    f"Error when loading doc with filetype {filetype}: '{err}'. "
                    f"Arguments: {kwargs}"
                )
            else:
                mess = (
                    f"Error when loading doc with filetype {filetype}: '{err}'. "
                    f"Arguments: {kwargs}"
                    f"\nLine number: {exc_tb.tb_lineno}"
                    f"\nFull traceback:\n{formatted_tb}"
                )
            if loading_failure == "crash":
                logger.exception(mess)
                raise Exception(mess) from err
            elif loading_failure == "warn" or env.WDOC_DEBUG:
                logger.warning(mess)
                return str(err)
            else:
                logger.exception(mess)
                raise ValueError(loading_failure) from err

    return wrapper


@wrapper_load_one_doc
def load_one_doc(
    task: str,
    llm_name: ModelName,
    temp_dir: Path,
    filetype: str,
    file_hash: str,
    source_tag: Optional[str] = None,
    doccheck_min_lang_prob: float = min_lang_prob,
    doccheck_min_token: int = min_token,
    doccheck_max_token: int = max_token,
    recur_parent_id: str = None,  # just used to keep track of which document comes from which recursive filetype
    subitem_link: str = None,
    **kwargs,
) -> List[Document]:
    """choose the appropriate loader for a file, then load it,
    split into documents, add some metadata then return.
    The loader is cached"""
    text_splitter = get_splitter(task, modelname=llm_name)
    assert kwargs, "Received an empty dict of arguments to load. Maybe --path is empty?"
    assert temp_dir.exists(), temp_dir

    # Check if filetype is supported
    if filetype not in FILETYPE_TO_LOADER:
        logger.warning(f"Unsupported filetype: '{filetype}'")
        raise Exception(f"Unsupported filetype: '{filetype}'")

    # Get the loader function name and retrieve the actual function
    loader_func_name = FILETYPE_TO_LOADER[filetype]
    loader_func = locals().get(loader_func_name) or globals().get(loader_func_name)

    if loader_func is None:
        raise Exception(
            f"Loader function '{loader_func_name}' not found for filetype '{filetype}'"
        )

    # Get function signature to determine what arguments to pass
    sig = inspect.signature(loader_func)

    # wdoc_global arguments (created by wdoc internally) - these are parameters of load_one_doc
    wdoc_global_args = {
        "task": task,
        "llm_name": llm_name,
        "temp_dir": temp_dir,
        "filetype": filetype,
        "file_hash": file_hash,
        "source_tag": source_tag,
        "doccheck_min_lang_prob": doccheck_min_lang_prob,
        "doccheck_min_token": doccheck_min_token,
        "doccheck_max_token": doccheck_max_token,
        "recur_parent_id": recur_parent_id,
        "text_splitter": text_splitter,
        "loaders_temp_dir": temp_dir,
        "verbose": env.WDOC_VERBOSE,
    }

    # User-provided arguments (from kwargs) - these come from user input
    user_args = kwargs

    # All available arguments
    available_args = {**wdoc_global_args, **user_args}

    # Get the parameter names of load_one_doc to distinguish wdoc_global vs user args
    load_one_doc_sig = inspect.signature(load_one_doc)
    wdoc_global_param_names = set(wdoc_global_args.keys())

    # Build arguments to pass to the loader function
    args_to_pass = {}
    missing_user_args = []
    missing_wdoc_global_args = []

    for param_name, param in sig.parameters.items():
        if param_name in available_args:
            args_to_pass[param_name] = available_args[param_name]
        elif param.default is param.empty:
            # Required parameter that we don't have - determine if it's wdoc_global or user arg
            if param_name in wdoc_global_param_names:
                # This should be provided by wdoc wdoc_global - indicates a bug
                missing_wdoc_global_args.append(param_name)
            else:
                # This should be provided by the user
                missing_user_args.append(param_name)

    # Check for unexpected user arguments that don't match function parameters
    unexpected_user_args = []
    for user_arg in user_args.keys():
        if user_arg not in sig.parameters:
            unexpected_user_args.append(user_arg)

    # Helper function to format arguments with their type hints and default values
    def format_args_with_types(arg_names: List[str]) -> str:
        formatted_lines = []
        for arg_name in arg_names:
            param = sig.parameters.get(arg_name)
            if param:
                # Build the argument description
                parts = [f"- {arg_name}"]

                # Add type hint if available
                if param.annotation != param.empty:
                    type_hint = param.annotation
                    # Always use the full string representation to show complete type hints
                    # like Literal["whisper", "deepgram"] instead of just "Literal"
                    type_str = str(type_hint)
                    parts.append(f": {type_str}")

                # Add default value if not required
                if param.default != param.empty:
                    parts.append(f" (default: {param.default})")

                formatted_lines.append("".join(parts))
            else:
                formatted_lines.append(f"- {arg_name}")

        return "\n".join(formatted_lines) if formatted_lines else ""

    if unexpected_user_args:
        valid_params = [
            param_name
            for param_name in sig.parameters.keys()
            if param_name not in wdoc_global_param_names
        ]
        formatted_valid_params = format_args_with_types(valid_params)
        raise MissingDocdictArguments(
            f"\n\nLoader function '{loader_func_name}' for filetype '{filetype}' "
            f"received unexpected arguments: {unexpected_user_args}\n"
            f"Valid user arguments for this loader are: {formatted_valid_params}\n"
            f"Please check the documentation for the correct arguments for this filetype."
        )

    # Get optional arguments with their types for better error messages
    optional_args = []
    for param_name, param in sig.parameters.items():
        if param.default is not param.empty and param_name not in available_args:
            optional_args.append(param_name)
    formatted_optional_args = format_args_with_types(optional_args)

    # Check for missing arguments
    if missing_wdoc_global_args and missing_user_args:
        # Both wdoc_global and user args are missing
        user_arg_names = list(user_args.keys()) if user_args else []
        formatted_wdoc_global_args = format_args_with_types(missing_wdoc_global_args)
        formatted_user_args = format_args_with_types(missing_user_args)
        raise MissingDocdictArguments(
            f"\n\nLoader function '{loader_func_name}' for filetype '{filetype}' "
            f"is missing required arguments from both wdoc wdoc_global and user input:\n"
            f"- Missing wdoc_global arguments (wdoc bug): {formatted_wdoc_global_args}\n"
            f"- Missing user arguments: {formatted_user_args}\n"
            f"You provided these arguments: {user_arg_names}.\n"
            f"Please check the documentation for the required arguments for this filetype and "
            f"create a GitHub issue at https://github.com/wdoc-ai/wdoc/issues with this error message."
        )
    elif missing_wdoc_global_args:
        # Only wdoc_global args are missing (wdoc bug)
        formatted_wdoc_global_args = format_args_with_types(missing_wdoc_global_args)
        optional_msg = (
            f"\n- Optional arguments available: {formatted_optional_args}"
            if formatted_optional_args
            else ""
        )
        raise MissingDocdictArguments(
            f"\n\nnInternal error: Loader function '{loader_func_name}' for filetype '{filetype}' "
            f"is missing required wdoc_global arguments: {formatted_wdoc_global_args}.{optional_msg}\n"
            f"This appears to be a wdoc bug - please create a GitHub issue at "
            f"https://github.com/wdoc-ai/wdoc/issues with this error message and your command."
        )
    elif missing_user_args:
        # Only user args are missing (user error)
        user_arg_names = list(user_args.keys()) if user_args else []
        formatted_user_args = format_args_with_types(missing_user_args)
        optional_msg = (
            f"\n- Optional arguments available: {formatted_optional_args}"
            if formatted_optional_args
            else ""
        )
        raise MissingDocdictArguments(
            f"\n\nLoader function '{loader_func_name}' for filetype '{filetype}' "
            f"is still missing required user arguments: {formatted_user_args}.{optional_msg}"
            f"\nYou provided these arguments: {user_arg_names}.\n"
            f"Please add the missing aguments or check the documentation for the required arguments for this filetype."
        )

    # Call the loader function with the appropriate arguments
    docs = loader_func(**args_to_pass)

    docs = text_splitter.transform_documents(docs)

    if filetype not in ["anki", "pdf"]:
        check_docs_tkn_length(
            docs=docs,
            identifier=filetype,
            min_lang_prob=doccheck_min_lang_prob,
            min_token=doccheck_min_token,
            max_token=doccheck_max_token,
        )

    # add and format metadata
    for i in range(len(docs)):
        # if html, parse it
        soup = bs4.BeautifulSoup(docs[i].page_content, "html.parser")
        if bool(soup.find()):
            docs[i].page_content = soup.get_text()

        # fix text just in case
        docs[i].page_content = ftfy.fix_text(docs[i].page_content)

        if source_tag:
            if "source_tag" not in docs[i].metadata:
                docs[i].metadata["source_tag"] = source_tag
            else:
                if not isinstance(docs[i].metadata["source_tag"], str):
                    docs[i].metadata["source_tag"] = str(docs[i].metadata["source_tag"])
                docs[i].metadata["source_tag"] = (
                    docs[i].metadata["source_tag"].replace("unset", "").strip()
                )
                docs[i].metadata["source_tag"] += f" {source_tag}"
        else:
            docs[i].metadata["source_tag"] = "unset"
        if "Author" in docs[i].metadata:
            docs[i].metadata["author"] = docs[i].metadata["Author"]
            del docs[i].metadata["Author"]
        if "authors" in docs[i].metadata:
            docs[i].metadata["author"] = docs[i].metadata["authors"]
            del docs[i].metadata["authors"]
        if "Authors" in docs[i].metadata:
            docs[i].metadata["author"] = docs[i].metadata["Authors"]
            del docs[i].metadata["Authors"]
        if "filetype" not in docs[i].metadata:
            docs[i].metadata["filetype"] = filetype
        if "path" not in docs[i].metadata and "path" in kwargs:
            docs[i].metadata["path"] = kwargs["path"]
        if subitem_link and "subitem_link" not in docs[i].metadata:
            docs[i].metadata["subitem_link"] = subitem_link
        if "title" not in docs[i].metadata or docs[i].metadata["title"] == "Untitled":
            if "title" in kwargs and kwargs["title"] and kwargs["title"] != "Untitled":
                docs[i].metadata["title"] = kwargs["title"]
            elif (
                "path" in docs[i].metadata
                and isinstance(docs[i].metadata["path"], str)
                and "http" in docs[i].metadata["path"].lower()
            ):
                docs[i].metadata["title"] = get_url_title(docs[i].metadata["path"])
                if not docs[i].metadata["title"]:
                    docs[i].metadata["title"] = "Untitled"
                    logger.debug(f"Could not get title from url of doc '{kwargs}'")
        if (
            "title" in kwargs
            and kwargs["title"] != docs[i].metadata["title"]
            and kwargs["title"] not in docs[i].metadata["title"]
        ):
            docs[i].metadata["title"] += " - " + kwargs["title"]
        if "playlist_title" in kwargs:
            docs[i].metadata["title"] = (
                kwargs["playlist_title"] + " - " + docs[i].metadata["title"]
            )

        if "doc_reading_time" not in docs[i].metadata:
            reading_length = len(docs[i].page_content) / average_word_length / wpm
            docs[i].metadata["doc_reading_time"] = round(reading_length, 3)
        if "source" not in docs[i].metadata:
            if "path" in docs[i].metadata:
                docs[i].metadata["source"] = docs[i].metadata["path"]
            elif "path" in docs[i].metadata:  # was probably not a path
                docs[i].metadata["source"] = docs[i].metadata["title"]
            else:
                docs[i].metadata["source"] = "undocumented"

        # make sure the filepath are absolute
        try:
            if "path" in docs[i].metadata and Path(docs[i].metadata["path"]).exists():
                docs[i].metadata["path"] = str(
                    Path(docs[i].metadata["path"]).resolve().absolute()
                )
        except Exception:
            pass  # was probably not a path

        docs[i].metadata["indexing_timestamp"] = int(time.time())

        # replace any path to just the filename, to avoid sending privacy
        # revealing information to LLMs
        for k, v in docs[i].metadata.items():
            if isinstance(v, Path):
                docs[i].metadata[k] = v.name

        # set hash
        docs[i].metadata["content_hash"] = hasher(docs[i].page_content)
        docs[i].metadata["file_hash"] = file_hash
        assert docs[i].metadata[
            "content_hash"
        ], f"Empty content_hash for document: {docs[i]}"
        assert docs[i].metadata["file_hash"], f"Empty file_hash for document: {docs[i]}"

        # check if metadata can be dumped, otherwise stringify the culprit
        try:
            meta_dump = json.dumps(docs[i].metadata, ensure_ascii=False)
        except Exception:
            for k, v in docs[i].metadata.items():
                if isinstance(v, Path):
                    docs[i].metadata[k] = v.name
                    continue
                try:
                    json.dumps(v, ensure_ascii=False)
                except Exception:
                    docs[i].metadata[k] = str(v)
            meta_dump = json.dumps(docs[i].metadata, ensure_ascii=False)

        docs[i].metadata["all_hash"] = hasher(
            docs[i].metadata["content_hash"] + meta_dump
        )
        assert docs[i].metadata["all_hash"], f"Empty all_hash for document: {docs[i]}"

    total_reading_length = None
    try:
        total_reading_length = sum(
            [float(d.metadata["doc_reading_time"]) for d in docs]
        )
    except Exception:
        pass
    if total_reading_length is not None:
        assert total_reading_length > 0.1, (
            f"Failing doc: total reading length is {total_reading_length:.3f}"
            "min which is  suspiciously low. Filetype {filetype} with kwargs "
            f"'{kwargs}'"
        )

    assert docs, "empty list of loaded documents!"
    return docs


# Convenience functions #########################


@memoize
def get_url_title(url: str) -> Union[str, type(None)]:
    """if the title of the url is not loaded from the loader, trying as last
    resort with this one"""
    loader = WebBaseLoader(url, raise_for_status=True)
    docs = loader.load()
    if "title" in docs[0].metadata and docs[0].metadata["title"]:
        return docs[0].metadata["title"]
    else:
        return None


def cloze_stripper(clozed: str) -> str:
    clozed = clozeregex.sub(" ", clozed)
    return clozed


# loaders #######################################


@debug_return_empty
@optional_strip_unexp_args
def load_youtube_video(
    path: str,
    loaders_temp_dir: Path,
    youtube_language: Optional[str] = None,
    youtube_translation: Optional[str] = None,
    youtube_audio_backend: Literal["youtube", "whisper", "deepgram"] = "youtube",
    whisper_lang: Optional[str] = None,
    whisper_prompt: Optional[str] = None,
    deepgram_kwargs: Optional[dict] = None,
) -> List[Document]:
    assert youtube_audio_backend in [
        "youtube",
        "whisper",
        "deepgram",
    ], f"Invalid value for youtube_audio_backend. Must be either youtube, whisper or deepgram, not '{youtube_audio_backend}'"

    if "\\" in path:
        logger.warning(f"Removed backslash found in '{path}'")
        path = path.replace("\\", "")

    if not yt_link_regex.search(path):
        logger.info(f"Not a youtube link but trying anyway: '{path}'")

    if youtube_audio_backend == "youtube":
        logger.info(f"Using youtube.com loader: '{path}'")
        try:
            docs = cached_yt_loader(
                path=path,
                add_video_info=True,
                language=(
                    [youtube_language] if youtube_language else ["en", "en-US", "en-UK"]
                ),
                translation=youtube_translation if youtube_translation else None,
            )
        except Exception as err:
            raise Exception(
                f"Error when using yt-dlp. Keep in mind that youtube frequently changed its backend so upgrading yt-dlp to its latest version can often fix issues. Original error was: '{err}'"
            ) from err
    else:
        logger.info(f"Downloading audio from url: '{path}'")
        file_name = (
            loaders_temp_dir / f"youtube_audio_{uuid6.uuid6()}"
        )  # without extension!
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            # with extension
            "outtmpl": f"{file_name.absolute().resolve()}.%(ext)s",
            "verbose": env.WDOC_VERBOSE,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([path])
        candidate = []
        for f in loaders_temp_dir.iterdir():
            if file_name.name in f.name:
                candidate.append(f)
        assert len(candidate), f"Audio file of {path} failed to download?"
        assert (
            len(candidate) == 1
        ), f"Multiple audio file found for video: '{candidate}'"
        audio_file = str(candidate[0].absolute())
        audio_hash = file_hasher({"path": audio_file})

        if youtube_audio_backend == "whisper":
            content = transcribe_audio_whisper(
                audio_path=audio_file,
                audio_hash=audio_hash,
                language=whisper_lang,
                prompt=whisper_prompt,
            )

            timestamped_text = convert_verbose_json_to_timestamped_text(content)

            docs = [
                Document(
                    page_content=timestamped_text,
                    metadata={
                        "source": "youtube_whisper",
                    },
                )
            ]
            if "duration" in content:
                docs[-1].metadata["duration"] = content["duration"]
            if "language" in content:
                docs[-1].metadata["language"] = content["language"]
            elif whisper_lang:
                docs[-1].metadata["language"] = whisper_lang

        elif youtube_audio_backend == "deepgram":
            content = transcribe_audio_deepgram(
                audio_path=audio_file,
                audio_hash=audio_hash,
                deepgram_kwargs=deepgram_kwargs,
            )
            assert (
                len(content["results"]["channels"]) == 1
            ), "unexpected deepgram output"
            assert (
                len(content["results"]["channels"][0]["alternatives"]) == 1
            ), "unexpected deepgram output"
            text = content["results"]["channels"][0]["alternatives"][0]["paragraphs"][
                "transcript"
            ].strip()
            assert text, "Empty text from deepgram transcription"

            docs = [
                Document(
                    page_content=text,
                    metadata={
                        "source": "youtube_deepgram",
                    },
                )
            ]
            docs[-1].metadata.update(content["metadata"])
            docs[-1].metadata["deepgram_kwargs"] = deepgram_kwargs

        else:
            raise ValueError(youtube_audio_backend)

        for f in Path(audio_file).parent.iterdir():
            if str(file_name.name) in f.stem:
                f.unlink()
        assert not Path(audio_file).exists()

    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache
def load_online_pdf(
    path: str,
    text_splitter: TextSplitter,
    file_hash: str,
    pdf_parsers: Union[str, List[str]] = "pymupdf",  # used only if online loading fails
    doccheck_min_lang_prob: float = min_lang_prob,
    doccheck_min_token: int = min_token,
    doccheck_max_token: int = max_token,
) -> List[Document]:
    logger.info(f"Loading online pdf: '{path}'")

    try:
        response = requests.get(path)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file.flush()

        docs = load_pdf(
            path=temp_file.name,
            text_splitter=text_splitter,
            file_hash=file_hasher({"path": temp_file.name}),
            pdf_parsers=pdf_parsers,
            doccheck_min_lang_prob=doccheck_min_lang_prob,
            doccheck_min_token=doccheck_min_token,
            doccheck_max_token=doccheck_max_token,
        )
        return docs

    except Exception as err:
        logger.warning(
            f"Failed parsing online PDF {path} by downloading it and trying to parse because of error '{err}'. Retrying one last time with OnlinePDFLoader."
        )
        loader = OnlinePDFLoader(path)
        if pdf_loader_max_timeout > 0:
            with signal_timeout(
                timeout=pdf_loader_max_timeout,
                exception=TimeoutPdfLoaderError,
            ):
                docs = loader.load()
            try:
                signal.alarm(0)  # disable alarm again just in case
            except Exception:
                pass
        else:
            docs = loader.load()

        return docs


@debug_return_empty
@optional_strip_unexp_args
def load_anki(
    verbose: bool,
    text_splitter: TextSplitter,
    loaders_temp_dir: Path,
    anki_profile: Optional[str] = None,
    anki_deck: Optional[str] = None,
    anki_notetype: Optional[str] = None,
    anki_template: Optional[str] = "{allfields}\n" + STR_IMAGE_OCR,
    anki_tag_filter: Optional[str] = None,
    anki_tag_render_filter: Optional[str] = None,
) -> List[Document]:
    if anki_tag_render_filter:
        assert (
            "{tags}" in anki_template
        ), "Can't use anki_tag_render_filter without using {tags} in anki_template"
        try:
            anki_tag_render_filter = re.compile(anki_tag_render_filter)
        except Exception as err:
            raise Exception(f"Failed to compile anki_tag_render_filter: '{err}'")

    if anki_tag_filter:
        try:
            anki_tag_filter = re.compile(anki_tag_filter)
        except Exception as err:
            raise Exception(f"Failed to compile anki_tag_filter: '{err}'")

    if not anki_profile:
        original_db = akp.find_db()
        anki_profile = original_db.parent.name
        logger.info(f"Detected anki profile: '{anki_profile}'")

    logger.info(f"Loading anki profile: '{anki_profile}'")
    original_db = akp.find_db(user=anki_profile)
    name = f"{anki_profile}".replace(" ", "_")
    random_val = str(uuid6.uuid6())
    new_db_path = (
        loaders_temp_dir / f"anki_collection_{name.replace('/', '_')}_{random_val}"
    )
    assert not Path(new_db_path).exists(), f"{new_db_path} already existing!"
    shutil.copy(original_db, new_db_path)
    col = akp.Collection(path=new_db_path)
    cards = col.cards.merge_notes()

    if verbose and not is_out_piped:
        tqdm.pandas()

        def pbar(*x, **y):
            tqdm.pandas(*x, **y)

    else:
        pd.DataFrame.progress_apply = pd.DataFrame.apply
        pd.Series.progress_apply = pd.Series.apply

        def pbar(*x, **y):
            pass

    cards.loc[cards["codeck"] == "", "codeck"] = cards["cdeck"][cards["codeck"] == ""]

    cards["codeck"] = cards["codeck"].progress_apply(lambda x: x.replace("\x1f", "::"))
    if anki_deck:
        cards = cards[cards["codeck"].str.startswith(anki_deck)]
    cards["nmodel"] = cards["nmodel"].progress_apply(lambda x: x.lower())
    if anki_notetype:
        cards = cards[cards["nmodel"].str.contains(anki_notetype, case=False)]
        assert (
            not cards.empty
        ), f"No cards found after filtering by notetype {anki_notetype}"
    if anki_tag_filter:
        pbar(desc="Filtering by tags")
        cards = cards[
            cards.progress_apply(
                (lambda x: any(anki_tag_filter.match(t) for t in x["ntags"])), axis=1
            )
        ]
        assert (
            not cards.empty
        ), f"No cards found after filtering by tags: {anki_tag_filter}"

    # remove suspended
    cards = cards[cards["cqueue"] != "suspended"]

    # merge models and fields for easy handling
    cards["mid"] = col.cards.mid.loc[cards.index]
    mid2fields = akp.raw.get_mid2fields(col.db)
    # make the model fields lowercase
    mid2fields = {
        k: (lambda x: [y.lower() for y in x])(v) for k, v in mid2fields.items()
    }
    # mod2mid = akp.raw.get_model2mid(col.db)
    cards["fields_name"] = cards["mid"].progress_apply(lambda x: mid2fields[x])
    assert not cards.empty, "empty dataframe!"

    # remove duplicate, essentially making cards the same thing as notes
    cards = cards.drop_duplicates(subset="nid", keep="first")
    notes = cards.reset_index().set_index("nid")

    # check placeholders validity
    placeholders = [ph.lower() for ph in anki_replacements_regex.findall(anki_template)]
    assert placeholders, f"No placeholder found in anki_template '{anki_template}'"
    for ph in placeholders:
        for ic, c in notes.iterrows():
            if ph not in c["fields_name"] + ["allfields", "tags", STR_IMAGE_OCR[1:-1]]:
                raise Exception(
                    "A placeholder in anki template didn't match fields of "
                    f"a card.\nCulprit placeholder: {ph}\nTemplate: "
                    f"{anki_template}\nExample card: {c}"
                )

    # prepare field values
    if "{allfields}" in anki_template:
        useallfields = True
        pbar(desc="Parsing allfields value")
        notes["allfields"] = notes.progress_apply(
            lambda x: "\n\n".join(
                [
                    f"{k.lower()}: '{html_to_text(cloze_stripper(v)).strip()}'"
                    for k, v in zip(x["fields_name"], x["nflds"])
                    if v.strip()
                ]
            ),
            axis=1,
        )
    else:
        useallfields = False

    if STR_IMAGE_OCR in anki_template:
        useimageocr = True
    else:
        useimageocr = False

    if "{tags}" in anki_template:
        usetags = True
        pbar(desc="Formatting tags")
        notes["tags_formatted"] = notes.progress_apply(
            lambda x: (
                (
                    "\n"
                    + "\n".join(
                        [
                            t
                            for t in x["ntags"]
                            if (
                                anki_tag_render_filter is None
                                or anki_tag_render_filter.match(t)
                            )
                        ]
                    ).strip()
                    + "\n"
                )
                if x["ntags"]
                else ""
            ),
            axis=1,
        )
        if notes["ntags"].notnull().any():
            assert (
                notes["tags_formatted"].notnull().any()
            ), "No tags were extracted because of your filter. Crashing to let you recheck your setup."
    else:
        usetags = False

    def placeholder_replacer(row: pd.Series) -> Tuple[str, dict]:
        text = anki_template

        if useallfields:
            text = text.replace("{allfields}", row["allfields"])
        if usetags:
            text = text.replace("{tags}", row["tags_formatted"])

        for ph in placeholders:
            if ph == "tags" or ph == "allfields" or ph == STR_IMAGE_OCR[1:-1]:
                continue
            field_val = row["nflds"][row["fields_name"].index(ph)]
            text = text.replace(
                "{" + ph + "}",
                html_to_text(
                    cloze_stripper(field_val),
                ),
            )
        text = text.replace("\\n", "\n").replace("\\xa0", " ")

        # replace media
        new_text, medias = replace_media(
            content=text,
            media=None,
            mode="remove_media",
            strict=False,
            replace_links=False,
        )
        if medias:
            assert text != new_text
        text = new_text
        if useimageocr:
            image_keys = [k for k in medias.keys() if "IMAGE" in k]
            for img_k in image_keys:
                img = bs4.BeautifulSoup(medias[img_k], "html.parser")
                title = img.get("title").strip() if img.has_attr("title") else ""
                alt = img.get("alt").strip() if img.has_attr("alt") else ""
                ocr_alt = ""
                if title:
                    ocr_alt += f"\nTitle: '{title}'"
                if alt:
                    ocr_alt += f"\nAlt: '{alt}'"
                ocr_alt = ocr_alt.strip()
                if ocr_alt:
                    text = text.replace(
                        STR_IMAGE_OCR,
                        f"\n<OCR of '{k}'>\n{ocr_alt}\n</OCR of '{k}'>" + STR_IMAGE_OCR,
                    )
            text = text.replace(STR_IMAGE_OCR, "").strip()

        return text, medias

    pbar(desc="Formatting all cards")
    notes["medias"] = {}
    out = notes.progress_apply(placeholder_replacer, axis=1)
    notes["text"] = [t[0] for t in out]
    notes["medias"] = [t[1] for t in out]

    notes["text"] = notes["text"].progress_apply(lambda x: x.strip())
    notes = notes[notes["text"].ne("")]  # remove empty text

    # remove notes that contain an image, sound or link
    # notes = notes[~notes["text"].str.contains("\[IMAGE_")]
    # notes = notes[~notes["text"].str.contains("\[SOUND_")]
    # notes = notes[~notes["text"].str.contains("\[LINK_")]

    notes["text"] = notes["text"].apply(lambda x: x.strip())
    notes = notes[notes["text"].ne("")]  # remove empty text
    notes.drop_duplicates(subset="text", inplace=True)

    notes = notes.sort_index()

    docs = []

    # load each card as a single document
    for nid, c in notes.iterrows():
        assert c["codeck"], f"empty card_deck for nid {nid}"
        # turn the media into absolute paths
        medias = c["medias"]
        to_add = {}
        for k, v in medias.items():
            assert (
                k in c["text"]
            ), f"missing media '{k}' in text '{c['text']}' of card '{c}'"
            try:
                src = bs4.BeautifulSoup(v, "html.parser").find("img")["src"]
                assert src
                v = Path(original_db).parent / "collection.media" / src
                v = v.resolve()
                if v.exists():
                    if k in c["text"]:
                        h = file_hasher({"path": str(v.absolute())})[:6]
                        placeholder = f"IMAGE_{h}"
                        medias[k] = None
                        to_add[placeholder] = str(v.absolute())
                        c["text"] = c["text"].replace(k, placeholder)
                    else:
                        medias[k] = str(v.absolute())
            except Exception:
                # it was probably not a file
                continue
        medias = {k: v for k, v in medias.items() if v is not None}
        if to_add:
            medias.update(to_add)
            assert all(k in c["text"] for k in to_add.keys())
        # better formatting for tags
        ntags = [
            nt
            # bettter for the tokenizer I guess
            # nt.replace("_", " ").replace("-", " ").replace("::", " > ")
            for nt in c["ntags"]
        ]
        docs.append(
            Document(
                page_content=c["text"],
                metadata={
                    "anki_tags": " ".join(ntags),
                    "anki_nid": str(nid),
                    "anki_deck": c["codeck"],
                    "anki_modtime": int(c["cmod"]),
                    "anki_media": json.dumps(medias, ensure_ascii=False),
                },
            )
        )

    assert docs, "List of loaded anki document is empty!"

    path = (
        f"Anki_profile='{anki_profile}',deck='{anki_deck}',notetype='{anki_notetype}'"
    )
    for i in range(len(docs)):
        docs[i].metadata["anki_profile"] = anki_profile
        docs[i].metadata["anki_topdeck"] = anki_deck
        docs[i].metadata["anki_notetype"] = anki_notetype
        docs[i].metadata["path"] = path
        docs[i].metadata["anki_nid"] = " ".join(
            sorted(docs[i].metadata["anki_nid"].split(" "))
        )

    # delete temporary db file
    new_db_path.unlink()
    Path(str(new_db_path.absolute()) + "-shm").unlink(missing_ok=True)
    Path(str(new_db_path.absolute()) + "-wal").unlink(missing_ok=True)
    return docs


REG_IMG = re.compile(r"<img .*?src=.*?/?>", flags=re.MULTILINE | re.DOTALL)

REG_SOUNDS = re.compile(
    r"\[sound:\w+\.\w{2,3}\]",
)
REG_LINKS = re.compile(
    r"[A-Za-z0-9]+://[A-Za-z0-9%-_]+(?:/[A-Za-z0-9%-_])*(?:#|\\?)[A-Za-z0-9%-_&=]*",
)


def replace_media(
    content: str,
    media: Union[None, Dict],
    mode: str,
    strict: bool = True,
    replace_image: bool = True,
    replace_links: bool = True,
    replace_sounds: bool = True,
) -> Tuple[str, Dict]:
    """
    Else: exclude any note that contains in the content:
        * an image (<img...)
        * or a sound [sound:...
        * or a link href / http
    This is because:
        1 as LLMs are non deterministic I preferred
            to avoid taking the risk of botching the content
        2 it costs less token

    The intended use is to call it first to replace
    each media by a simple string like [IMAGE_1] and check if it's
    indeed present in the output of the LLM then replace it back.

    It uses both bs4 and regex to be sure of itself
    """
    # ignore warnings from beautiful soup that can happen because anki is not exactly html
    warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

    assert mode in ["add_media", "remove_media"]
    assert content.strip()
    if media is None:
        media = {}
    assert isinstance(media, dict)
    assert any(rule for rule in [replace_sounds, replace_links, replace_image])

    if mode == "remove_media":
        assert not media
        images = []
        sounds = []
        links = []

        if replace_links:
            # fix links common issues
            content = content.replace(":// ", "://")
            content = content.replace("http ://", "http://")
            content = content.replace("https ://", "http://")

        # Images
        if replace_image and "<img" in content:
            soup = bs4.BeautifulSoup(content, "html.parser")
            images_bs4 = [str(img) for img in soup.find_all("img")]
            # fix bs4 parsing as ending with /> instead of >
            images_bs4 = [
                (
                    img[:-2] + ">"
                    if ((img not in content) and img[:-2] + ">" in content)
                    else img
                )
                for img in images_bs4
            ]
            images_reg = re.findall(REG_IMG, content)
            if len(images_bs4) != len(images_reg):
                if env.WDOC_VERBOSE:
                    logger.warning(
                        f"Different images found:\nbs4: {images_bs4}\nregex: {images_reg}\nContent: {content}"
                    )
                if images_bs4 and not images_reg:
                    images = [str(img) for img in images_bs4]
                elif (not images_bs4) and images_reg:
                    images = [str(img) for img in images_reg]
            else:
                images = [str(img) for img in images_bs4]
            try:
                assert images, f"no image found but should have. Text is '{content}'"
            except AssertionError as err:
                if strict:
                    raise
                logger.warning(err)
            for iimg, img in enumerate(images):
                try:
                    assert (
                        img in content
                    ), f"missing img from content:\nimg: {img}\ncontent: {content}"
                    assert re.search(
                        REG_IMG, img
                    ), f"Regex couldn't identify img: {img}"
                    assert not re.search(
                        REG_SOUNDS, img
                    ), f"Sound regex identifier img: {img}"
                except AssertionError as err:
                    if strict:
                        raise
                    logger.warning(err)
                    images[iimg] = None
            images = [i for i in images if i is not None]
            images = list(set(images))

        # Sounds
        if replace_sounds and "[sounds:" in content:
            sounds = re.findall(REG_SOUNDS, content)
            try:
                assert sounds, f"No sounds found but should have. Content: {content}"
            except AssertionError as err:
                if strict:
                    raise
                logger.warning(err)
            for isound, sound in enumerate(sounds):
                try:
                    assert sound in content, f"Sound is not in content: {sound}"
                    assert not re.search(
                        REG_IMG, sound
                    ), f"Image regex identified this sound: {sound}"
                    assert re.search(
                        REG_SOUNDS, sound
                    ), f"Regex didn't identify this sound: {sound}"
                except AssertionError as err:
                    if strict:
                        raise
                    logger.warning(err)
                    sounds[isound] = None
            sounds = [s for s in sounds if s is not None]
            sounds = list(set(sounds))

        # links
        if replace_links and "://" in content:
            links = re.findall(REG_LINKS, content)
            links = [
                link
                for link in links
                if not any(other != link and other in link for other in links)
            ]
            if strict:
                assert links, "No links found"
            for ilink, link in enumerate(links):
                try:
                    assert (
                        link in content
                    ), f"Link not in content:\nlink: {link}\ncontent: {content}"
                    assert re.search(
                        REG_LINKS, link
                    ), f"Regex couldn't identify link: {link}"
                except AssertionError as err:
                    if strict:
                        raise
                    logger.warning(err)
                    links[ilink] = None
            links = [li for li in links if li is not None]
            links = list(set(links))

        if not images + sounds + links:
            return content, {}

        new_content = content

        # do the replacing
        for i, img in enumerate(images):
            assert replace_image, replace_image
            try:
                assert img in content, f"img '{img}' not in content '{content}'"
                assert (
                    img in new_content
                ), f"img '{img}' not in new_content '{new_content}'"
                assert img not in media.keys() and img not in media.values()
                replaced = f"[IMAGE_{i+1}]"
                assert replaced not in media.keys() and replaced not in media.values()
                assert (
                    replaced not in content
                ), f"Replaced '{replaced}' already in content '{content}'"
                assert (
                    replaced not in new_content
                ), f"Replaced '{replaced}' already in new_content '{new_content}'"
                new_content = new_content.replace(img, replaced)
                media[replaced] = img
                assert img not in new_content
                assert replaced in new_content
            except AssertionError as err:
                if strict:
                    raise
                logger.warning(f"Failed assert when replacing image: '{err}'")
                continue

        for i, sound in enumerate(sounds):
            try:
                assert replace_sounds
                assert sound in content
                assert sound in new_content
                assert sound not in media.keys() and sound not in media.values()
                replaced = f"[SOUND_{i+1}]"
                assert replaced not in media.keys() and replaced not in media.values()
                assert replaced not in content
                assert replaced not in new_content
                new_content = new_content.replace(sound, replaced)
                media[replaced] = sound
                assert sound not in new_content
                assert replaced in new_content
            except AssertionError as err:
                if strict:
                    raise
                logger.warning(f"Failed assert when replacing sounds: '{err}'")
                continue

        for i, link in enumerate(links):
            try:
                assert replace_links
                assert link in content
                assert link not in media.keys()
                replaced = f"[LINK_{i+1}]"
                assert replaced not in media.keys() and replaced not in media.values()
                assert replaced not in content
                assert replaced not in new_content
                assert link in new_content or len(
                    [val for val in media.values() if link in val]
                )
                if link not in new_content:
                    continue
                else:
                    new_content = new_content.replace(link, replaced)
                    media[replaced] = link
                    assert link not in new_content
                    assert replaced in new_content
            except AssertionError as err:
                if strict:
                    raise
                logger.warning(f"Failed assert when replacing links: '{err}'")
                continue

        # check no media can be found anymore
        if replace_image:
            if strict:
                assert not re.findall(REG_IMG, new_content), new_content
                assert not bs4.BeautifulSoup(new_content, "html.parser").find_all(
                    "img"
                ), new_content
                assert "<img" not in new_content, new_content
            elif "<img" in new_content:
                logger.warning(f"AnkiMediaReplacer: Found '<img' in '{new_content}'")
        if replace_sounds:
            if strict:
                assert not re.findall(REG_SOUNDS, new_content), new_content
                assert "[sound:" not in new_content, new_content
            elif "[sound:" in new_content:
                logger.warning(f"AnkiMediaReplacer: Found '[sound:' in '{new_content}'")
        if replace_links:
            if strict:
                assert not re.findall(REG_LINKS, new_content), new_content
                assert "://" not in new_content, new_content
            elif "://" in new_content:
                logger.warning(f"AnkiMediaReplacer: Found '://' in '{new_content}'")

        # check non empty
        temp = new_content
        for med, val in media.items():
            temp = temp.replace(med, "")
        assert temp.strip()

        # recursive check:
        assert (
            replace_media(
                content=new_content,
                media=media,
                mode="add_media",
                strict=strict,
                replace_image=replace_image,
                replace_links=replace_links,
                replace_sounds=replace_sounds,
            )[0]
            == content
        )

        return new_content, media

    elif mode == "add_media":
        assert media

        # TODO check that all media are found
        new_content = content
        for med, val in media.items():
            assert med in content
            assert val not in content
            assert val not in new_content
            new_content = new_content.replace(med, val)
            assert med not in new_content
            assert val in new_content

        return new_content, {}

    else:
        raise ValueError(mode)


@debug_return_empty
def load_string() -> List[Document]:
    logger.info("Loading string")
    content = prompt(
        "Paste your text content here then press esc+enter or meta+enter:\n>",
        multiline=True,
    )
    logger.info(f"Pasted string input:\n{content}")
    docs = [
        Document(
            page_content=content,
            metadata={"path": "user_string"},
        )
    ]
    return docs


@debug_return_empty
@optional_strip_unexp_args
def load_txt(path: Union[str, Path], file_hash: str) -> List[Document]:
    path = Path(path)
    logger.info(f"Loading txt: '{path}'")
    assert path.exists(), f"file not found: '{path}'"
    content = path.read_text()
    docs = [Document(page_content=content, metadata={})]
    return docs


@debug_return_empty
@optional_strip_unexp_args
def load_text_input(
    path: str,
    file_hash: str,
    metadata: Optional[Union[str, dict]] = None,
) -> List[Document]:
    logger.info(f"Loading text input: '{path}'")
    text = path.strip()
    assert text, "Empty text"
    if metadata is None:
        metadata = {}
    if isinstance(metadata, str):
        metadata = json.loads(metadata)

    docs = [
        Document(
            page_content=text,
            metadata=metadata,
        )
    ]
    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_local_html(
    path: Union[str, Path],
    file_hash: str,
    load_functions: Optional[bytes] = None,
) -> List[Document]:
    path = Path(path)
    logger.info(f"Loading local html: '{path}'")
    assert path.exists(), f"file not found: '{path}'"

    content = path.read_text()

    if load_functions:
        # the functions must be pickled because joblib can't
        # cache string that would declare as lambda functions

        try:
            load_functions = dill.loads(load_functions)
        except Exception as err:
            raise Exception(f"Error when unpickling load_functions: '{err}'")
        assert isinstance(
            load_functions, tuple
        ), f"load_functions must be a tuple, not {type(load_functions)}"
        assert all(
            callable(lf) for lf in load_functions
        ), f"load_functions element must be a callable, not {[type(lf) for lf in load_functions]}"

        for ifunc, func in enumerate(load_functions):
            try:
                content = func(content)
            except Exception as err:
                raise Exception(
                    f"load_functions #{ifunc}: '{func}' failed with " f"error : '{err}'"
                )
        assert isinstance(content, str), (
            f"output of function #{ifunc}: '{func}' is not a " f"string: {content}"
        )
    try:
        soup = bs4.BeautifulSoup(content, "html.parser")
    except Exception as err:
        raise Exception(f"Error when parsing html: {err}")

    text = soup.get_text().strip()
    assert text, "Empty text after loading from html"

    docs = [
        Document(
            page_content=text,
        )
    ]
    return docs


@doc_loaders_cache.cache
def eval_load_functions(
    load_functions: str,
) -> List[Callable]:
    assert isinstance(load_functions, list), "load_functions must be of type list"
    assert all(
        isinstance(lf, str) for lf in load_functions
    ), "elements of load_functions must be of type str"

    try:
        for ilf, lf in enumerate(load_functions):
            load_functions[ilf] = eval(lf)
    except Exception as err:
        raise Exception(f"Error when evaluating load_functions #{ilf}: {lf} '{err}'")
    assert all(
        callable(lf) for lf in load_functions
    ), f"Some load_functions are not callable: {load_functions}"


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_logseq_markdown(
    path: Union[str, Path],
    file_hash: str,
    text_splitter: TextSplitter,
) -> List[Document]:
    path = Path(path)
    logger.info(f"Loading logseq markdown file: '{path}'")
    assert path.exists(), f"file not found: '{path}'"
    try:
        parsed = LogseqMarkdownParser.parse_file(path, verbose=False)
    except Exception as err:
        raise Exception(f"Error when parsing {path} LogseqMarkdownParser: '{err}'")

    if not parsed.blocks:
        raise Exception(
            f"No logseq blocks loaded for {path} (file size: {Path(path).stat().st_size})"
        )

    blocks = parsed.blocks
    page_props = parsed.page_properties

    content = parsed.content
    content = content.replace("\t", "    ")
    content = markdownimage_regex.sub("[IMAGE]", content)
    # content, _ = replace_media(
    #     content=content,
    #     media=None,
    #     mode="remove_media",
    #     strict=False,
    #     replace_image=True,
    #     replace_links=True,
    #     replace_sounds=False,
    # )

    # create a single document then for each document add the properties of each block found in the doc
    docs = text_splitter.transform_documents(
        [
            Document(
                page_content=content,
                metadata=page_props,
            )
        ]
    )

    failed_blocks = []
    for b in blocks:
        b = copy.copy(b)
        props = b.properties.copy()
        for k, v in props.items():
            b.del_property(key=k)
            b.content = b.content.strip()
        cont = b.content.replace("\t", "    ")
        cont = markdownimage_regex.sub("[IMAGE]", cont)
        # cont, _ = replace_media(
        #     content=cont,
        #     media=None,
        #     mode="remove_media",
        #     strict=False,
        #     replace_image=True,
        #     replace_links=True,
        #     replace_sounds=False,
        # )
        if not cont:
            continue
        found = False
        for i, d in enumerate(docs):
            if i + 1 >= len(docs):
                next = ""
            else:
                next = docs[i + 1].page_content
            if cont.strip() in d.page_content or (
                cont not in next and cont in d.page_content + next
            ):

                # merge metadata dictionnaries
                for k, v in props.items():
                    if not v:
                        continue
                    if k not in docs[i].metadata:
                        docs[i].metadata[k] = v
                    elif docs[i].metadata[k] == v:
                        continue
                    elif isinstance(docs[i].metadata[k], list):
                        if isinstance(v, list):
                            docs[i].metadata[k].extend(v)
                        else:
                            docs[i].metadata[k].append(v)
                    else:
                        assert k in docs[i].metadata
                        assert not isinstance(docs[i].metadata[k], list)
                        assert docs[i].metadata[k] != v
                        if isinstance(v, list):
                            docs[i].metadata[k] = [docs[i].metadata[k]] + v
                        else:
                            docs[i].metadata[k] = [docs[i].metadata[k], v]
                found = True
                break
        if not found:
            failed_blocks.append(b)

    if failed_blocks:
        mess = f"Couldn't find {len(failed_blocks)} block(s) out of {len(blocks)} after splitting the logseq page."
        mess += "\nBlocks were:"
        for b in failed_blocks:
            mess += "\n" + str(b)
        if len(failed_blocks) >= 0.5 * len(blocks):
            mess += "\nMissing more than 50% of blocks so crashing"
            raise Exception(mess)
        else:
            logger.warning(mess + "\nBut continuing nonetheless")

    # sort and deduplicate metadata
    for i, d in enumerate(docs):
        for k, v in d.metadata.items():
            if isinstance(v, list):
                d.metadata[k] = list(sorted(list(set(v))))
            assert d.metadata[
                k
            ], f"There shouldn't be any empty metadata value but key '{k}' of doc '{d}' is empty."

    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_local_audio(
    path: Union[str, Path],
    file_hash: str,
    audio_backend: Literal["whisper", "deepgram"],
    loaders_temp_dir: Path,
    audio_unsilence: bool = True,
    whisper_lang: Optional[str] = None,
    whisper_prompt: Optional[str] = None,
    deepgram_kwargs: Optional[dict] = None,
) -> List[Document]:
    path = Path(path)
    assert path.exists(), f"file not found: '{path}'"

    if audio_unsilence:
        logger.warning(f"Removing silence from audio file {path.name}")
        waveform, sample_rate = torchaudio.load(path)

        dur = waveform.shape[1] / sample_rate
        start = time.time()
        try:
            waveform, sample_rate = torchaudio.sox_effects.apply_effects_tensor(
                waveform,
                sample_rate,
                sox_effects,
            )
        except Exception as e:
            if "libsox.so" in str(e).lower():
                logger.exception(
                    "The error hints at not being able to find libsox.so, on linux this can be solved by installing libsox-dev"
                )
            logger.warning(
                f"Error when applying sox effects: '{e}'.\nRetrying to apply each filter individually."
            )
            for sef in sox_effects:
                nfailed = 0
                logger.info(f"Applying filter '{sef}'")
                try:
                    waveform, sample_rate = torchaudio.sox_effects.apply_effects_tensor(
                        waveform,
                        sample_rate,
                        [sef],
                    )
                except Exception as err:
                    logger.warning(f"Error when applying sox effects '{sef}': {err}")
                    nfailed += 1
                if nfailed == len(sox_effects):
                    raise Exception(
                        "All sox_effects failed, you should report this bug and turn off --audio_unsilence"
                    )
        elapsed = time.time() - start
        new_dur = waveform.shape[1] / sample_rate

        if new_dur == dur:
            logger.warning(
                f"Duration of audio has not changed when trying to remove silence, something probably went wrong. Duration: {new_dur}"
            )
            # will crash anyway at the folling line because the assert is strict

        assert new_dur < dur, (
            f"Failed to remove silence for {path.name}:\n"
            f"Original duration: {dur:.1f}\n"
            f"New duration: {new_dur:.1f}\n"
        )
        assert new_dur > 10, (
            f"Silence removal ended up with a suspiciously short audio for {path.name}:\n"
            f"Original duration: {dur:.1f}\n"
            f"New duration: {new_dur:.1f}\n"
        )
        logger.warning(
            f"Removed silence from {path.name}: {dur:.1f} -> {new_dur:.1f} in {elapsed:.1f}s"
        )

        unsilenced_path_wav = loaders_temp_dir / f"unsilenced_audio_{uuid6.uuid6()}.wav"
        unsilenced_path_ogg = loaders_temp_dir / f"unsilenced_audio_{uuid6.uuid6()}.ogg"
        assert not unsilenced_path_wav.exists()
        assert not unsilenced_path_ogg.exists()
        torchaudio.save(
            uri=str(unsilenced_path_wav.resolve().absolute()),
            src=waveform,
            sample_rate=sample_rate,
            format="wav",
        )
        # turn the .wav into .ogg
        ffmpeg.input(str(unsilenced_path_wav.resolve().absolute())).output(
            str(unsilenced_path_ogg.resolve().absolute())
        ).run()
        unsilenced_hash = file_hasher({"path": unsilenced_path_ogg})

        # old_path = path
        # old_hash = file_hash
        path = unsilenced_path_ogg
        file_hash = unsilenced_hash

    if audio_backend == "whisper":
        assert (
            deepgram_kwargs is None
        ), "Found kwargs for deepgram but selected whisper backend for local_audio"
        content = transcribe_audio_whisper(
            audio_path=path,
            audio_hash=file_hash,
            language=whisper_lang,
            prompt=whisper_prompt,
        )
        timestamped_text = convert_verbose_json_to_timestamped_text(content)
        docs = [
            Document(
                page_content=timestamped_text,
                metadata={
                    "source": str(Path(path)),
                },
            )
        ]
        if "duration" in content:
            docs[-1].metadata["duration"] = content["duration"]
        if "language" in content:
            docs[-1].metadata["language"] = content["language"]
        elif whisper_lang:
            docs[-1].metadata["language"] = whisper_lang

    elif audio_backend == "deepgram":
        assert (
            whisper_prompt is None and whisper_lang is None
        ), "Found args whisper_prompt or whisper_lang but selected deepgram backend for local_audio"
        content = transcribe_audio_deepgram(
            audio_path=path,
            audio_hash=file_hash,
            deepgram_kwargs=deepgram_kwargs,
        )
        assert len(content["results"]["channels"]) == 1, "unexpected deepgram output"
        assert (
            len(content["results"]["channels"][0]["alternatives"]) == 1
        ), "unexpected deepgram output"
        text = content["results"]["channels"][0]["alternatives"][0]["paragraphs"][
            "transcript"
        ].strip()
        assert text, "Empty text from deepgram transcription"

        docs = [
            Document(
                page_content=text,
                metadata={
                    "source": "local_audio_deepgram",
                },
            )
        ]
        docs[-1].metadata.update(content["metadata"])
        docs[-1].metadata["deepgram_kwargs"] = deepgram_kwargs

    else:
        raise ValueError(
            f"Invalid audio backend: must be either 'deepgram' or 'whisper'. Not '{audio_backend}'"
        )

    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_local_video(
    path: Union[str, Path],
    file_hash: str,
    audio_backend: Literal["whisper", "deepgram"],
    loaders_temp_dir: Path,
    audio_unsilence: bool = True,
    whisper_lang: Optional[str] = None,
    whisper_prompt: Optional[str] = None,
    deepgram_kwargs: Optional[dict] = None,
) -> List[Document]:
    path = Path(path)
    assert path.exists(), f"file not found: '{path}'"

    audio_path = loaders_temp_dir / f"audio_from_video_{uuid6.uuid6()}.mp3"
    assert not audio_path.exists()

    # extract audio from video
    try:
        logger.info(
            f"Exporting audio from {path} to {audio_path} (this can take some time)"
        )
        t = time.time()
        ffmpeg.input(path).output(str(audio_path.resolve().absolute())).run()
        logger.info(f"Done extracting audio in {time.time()-t:.2f}s")
    except Exception as err:
        logger.warning(
            f"Error when getting audio from video using ffmpeg. Retrying with pydub. Error: '{err}'"
        )

        try:
            Path(audio_path).unlink(missing_ok=True)
            audio = pydub.AudioSegment.from_file(path)
            # extract audio from video
            logger.info(
                f"Extracting audio from {path} to {audio_path} (this can take some time)"
            )
            t = time.time()
            audio.export(audio_path, format="mp3")
            logger.info(f"Done extracting audio in {time.time()-t:.2f}s")
        except Exception as err:
            raise Exception(
                f"Error when getting audio from video using ffmpeg: '{err}'"
            )

    assert Path(audio_path).exists(), f"FileNotFound: {audio_path}"

    # need the hash from the mp3, not video
    audio_hash = file_hasher({"path": audio_path})

    sub_loaders_temp_dir = loaders_temp_dir / "local_audio"
    sub_loaders_temp_dir.mkdir()

    return load_local_audio(
        path=audio_path,
        loaders_temp_dir=sub_loaders_temp_dir,
        file_hash=audio_hash,
        audio_backend=audio_backend,
        whisper_lang=whisper_lang,
        whisper_prompt=whisper_prompt,
        deepgram_kwargs=deepgram_kwargs,
        audio_unsilence=audio_unsilence,
    )


@doc_loaders_cache.cache(ignore=["audio_path"])
def transcribe_audio_deepgram(
    audio_path: Union[str, Path],
    audio_hash: str,
    deepgram_kwargs: Optional[dict] = None,
) -> dict:
    "Use whisper to transcribe an audio file"
    logger.info(f"Calling deepgram to transcribe {audio_path}")
    assert (
        not env.WDOC_PRIVATE_MODE
    ), "Private mode detected, aborting before trying to use deepgram's API"
    assert (
        "DEEPGRAM_API_KEY" in os.environ
        and not os.environ["DEEPGRAM_API_KEY"]
        == "REDACTED_BECAUSE_WDOC_IN_PRIVATE_MODE"
    ), "No environment variable DEEPGRAM_API_KEY found"

    # client
    try:
        client = deepgram.DeepgramClient()
    except Exception as err:
        raise Exception(f"Error when creating deepgram client: '{err}'")

    # set options
    options = dict(
        # docs: https://playground.deepgram.com/?endpoint=listen&smart_format=true&language=en&model=nova-3
        model="nova-3",
        detect_language=True,
        # not all features below are available for all languages
        # intelligence
        summarize=False,
        topics=False,
        intents=False,
        sentiment=False,
        # transcription
        smart_format=True,
        punctuate=True,
        paragraphs=True,
        utterances=True,
        diarize=True,
        # redact=None,
        # replace=None,
        # search=None,
        # keywords=None,
        # filler_words=False,
    )
    if deepgram_kwargs is None:
        deepgram_kwargs = {}
    if "language" in deepgram_kwargs and deepgram_kwargs["language"]:
        del options["detect_language"]
    options.update(deepgram_kwargs)
    options = deepgram.PrerecordedOptions(**options)

    # load file
    with open(audio_path, "rb") as f:
        payload = {"buffer": f.read()}

    # get content
    t = time.time()
    content = client.listen.prerecorded.v("1").transcribe_file(
        payload,
        options,
        timeout=httpx.Timeout(300.0, connect=10.0),  # timeout for large files
    )
    logger.info(f"Done deepgram transcribing {audio_path} in {int(time.time()-t)}s")
    d = content.to_dict()
    return d


@doc_loaders_cache.cache(ignore=["audio_path"])
def transcribe_audio_whisper(
    audio_path: Union[Path, str],
    audio_hash: str,
    language: Optional[str],
    prompt: Optional[str],
) -> dict:
    "Use whisper to transcribe an audio file"
    logger.info(f"Calling openai's whisper to transcribe {audio_path}")
    if env.WDOC_PRIVATE_MODE:
        assert (
            env.WDOC_WHISPER_ENDPOINT
        ), "WDOC_PRIVATE_MODE is set but no WDOC_WHISPER_ENDPOINT is set. Crashing as it seems like your private request would call a remote API"
        assert (
            not os.environ["WDOC_WHISPER_API_KEY"]
            == "REDACTED_BECAUSE_WDOC_IN_PRIVATE_MODE"
        ), "No environment variable WDOC_WHISPER_API_KEY found"
    else:
        assert (
            "OPENAI_API_KEY" in os.environ
            and not os.environ["OPENAI_API_KEY"]
            == "REDACTED_BECAUSE_WDOC_IN_PRIVATE_MODE"
        ), "No environment variable OPENAI_API_KEY found"

    try:
        t1 = time.time()
        with open(audio_path, "rb") as audio_file:
            # Prepare transcription arguments
            transcription_kwargs = {
                "model": env.WDOC_WHISPER_MODEL,
                "file": audio_file,
                "prompt": prompt,
                "language": language,
                "temperature": 0,
                "response_format": "verbose_json",
            }

            # Add custom endpoint and API key if provided
            if env.WDOC_WHISPER_ENDPOINT:
                transcription_kwargs["api_base"] = env.WDOC_WHISPER_ENDPOINT
                logger.debug(
                    f"Using custom whisper endpoint: {env.WDOC_WHISPER_ENDPOINT}"
                )

            if env.WDOC_WHISPER_API_KEY:
                transcription_kwargs["api_key"] = env.WDOC_WHISPER_API_KEY
                logger.debug("Using custom whisper API key")

            try:
                transcript = litellm.transcription(**transcription_kwargs).json()
            except Exception as litellm_err:
                logger.warning(
                    f"litellm.transcription failed with error: {litellm_err}. "
                    f"Falling back to direct requests call to whisper endpoint."
                )

                # Fallback to direct requests call
                if not env.WDOC_WHISPER_ENDPOINT:
                    raise Exception(
                        "litellm failed and no WDOC_WHISPER_ENDPOINT set for fallback"
                    ) from litellm_err

                # Prepare the multipart form data
                files = {"file": audio_file}
                data = {
                    "model": env.WDOC_WHISPER_MODEL,
                    "response_format": "verbose_json",
                    "temperature": 0,
                }

                if prompt:
                    data["prompt"] = prompt
                if language:
                    data["language"] = language

                headers = {}
                if env.WDOC_WHISPER_API_KEY:
                    headers["Authorization"] = f"Bearer {env.WDOC_WHISPER_API_KEY}"

                # Make the request
                endpoint_url = (
                    env.WDOC_WHISPER_ENDPOINT.rstrip("/") + "/v1/audio/transcriptions"
                )
                response = requests.post(
                    endpoint_url, files=files, data=data, headers=headers
                )
                response.raise_for_status()
                transcript = response.json()

        t2 = time.time()
        logger.info(f"Done transcribing {audio_path} in {int(t2-t1)}s")

    except Exception as e:
        if "Maximum content size limit" in str(e):
            audio_splits = split_too_large_audio(audio_path)

            # reconstitute appropriate durations
            transcripts = []

            if env.WDOC_WHISPER_PARALLEL_SPLITS:
                logger.info(f"Processing {len(audio_splits)} audio splits in parallel")

                def process_audio_split(f: Path) -> dict:
                    """Process a single audio split file."""
                    h = file_hasher({"path": f})
                    return transcribe_audio_whisper(
                        audio_path=f,
                        audio_hash=h,
                        language=language,
                        prompt=prompt,
                    )

                # Process splits in parallel using joblib
                transcripts = joblib.Parallel(
                    n_jobs=-1,
                    backend="threading",
                )(joblib.delayed(process_audio_split)(f) for f in audio_splits)
            else:
                logger.warning(
                    "Using sequential processing for whisper over audio splits"
                )

                for f in audio_splits:
                    h = file_hasher({"path": f})
                    temp = transcribe_audio_whisper(
                        audio_path=f,
                        audio_hash=h,
                        language=language,
                        prompt=prompt,
                    )
                    transcripts.append(temp)

            if len(transcripts) == 1:
                return transcripts[0]

            logger.info(f"Combining {len(transcripts)} audio splits into a single json")
            ref = transcripts.pop(0)
            if ref["words"] is not None:
                logger.warning(
                    "Warning: the transcript contains a 'words' output, which will be discarded as the combination of word timestamps is not yet supported."
                )
                ref["words"] = None
            for itrans, trans in enumerate(transcripts):
                assert trans["task"] == ref["task"]
                if trans["language"] != ref["language"]:
                    logger.warning(
                        f"Warning: the language of the reference split audio ({ref['language']}) is not the same as the language of the current split ({trans['language']})"
                    )
                if trans["words"] is not None:
                    logger.warning(
                        "Warning: the transcript contains a 'words' output, which will be discarded as the combination of word timestamps is not yet supported."
                    )
                    trans["words"] = None

                temp = trans["segments"]
                for it, t in enumerate(temp):
                    temp[it]["end"] += ref["duration"]
                    temp[it]["start"] += ref["duration"]

                ref["segments"].extend(temp)

                ref["duration"] += trans["duration"]
                ref["text"] += " [note: audio was split here] " + trans["text"]

            return ref

        else:
            raise
    return transcript


def split_too_large_audio(
    audio_path: Union[Path, str],
) -> List[Path]:
    """Whisper has a file size limit of about 25mb. If we hit that limit, we
    split the audio file into multiple 30 minute files, then combine the
    outputs
    """
    audio_path = Path(audio_path)
    logger.info(
        f"Splitting large audio file '{audio_path}' into 30minute segment because it's too long for whisper"
    )
    split_folder = audio_path.parent / (audio_path.stem + "_splits")
    split_folder.mkdir(exist_ok=False)
    ext = audio_path.suffix

    ffmpeg.input(str(audio_path.absolute())).output(
        str((split_folder / f"split__%03d.{ext}").absolute()),
        c="copy",
        f="segment",
        segment_time=1600,  # 30 minute by default
    ).run()
    split_files = [f for f in split_folder.iterdir()]
    assert split_files
    return split_files


def process_vtt_content_for_llm(
    vtt_content: str, remove_hour_prefix: bool = True
) -> str:
    """
    Process VTT content to make it more suitable for LLMs by reducing timecodes
    and removing unnecessary formatting.

    Args:
        vtt_content: The VTT content to process
        remove_hour_prefix: Whether to remove "00:" hour prefix if all content is under 99 minutes

    Returns:
        Processed text content optimized for LLM consumption
    """
    # Reduce greatly the number of token in the subtitles by removing some less important formatting
    lines = vtt_content.splitlines()
    timecode_pattern = re.compile(
        r"(?:\d{2}:\d{2}:\d{2}\.\d{3})|(?:<\d{2}:\d{2}:\d{2}\.\d{3}>)|(?:</?c>)"
    )
    latest_tc = -1  # store the timecode once every Xs
    newlines = []

    for li in lines:
        if " --> " in li:
            li = re.sub(r"\.\d+ -->.*", "", li).strip()

            # remove duplicate timecodes:
            tc = timecode_to_second(li)
            if tc - latest_tc < 15:
                li = ""
            else:
                latest_tc = tc
        else:
            li = timecode_pattern.sub("", li).strip()

        is_tc = is_timecode(li)

        # We need at least one line, but skeep the lines before the first timecode
        if not newlines:
            if is_tc:
                newlines.append(li)
            continue

        # Check no consecutive timecodes (for cached_yt_loader compatibility)
        elif len(newlines) >= 2:
            if is_tc and is_timecode(newlines[-1]):
                # Skip consecutive timecodes to avoid VTT format issues
                continue

        if is_tc:
            newlines.append(li + " ")
        elif is_timecode(newlines[-1]):
            newlines[-1] += " " + li.strip()
        elif li not in newlines[-1]:
            newlines[-1] += " " + li.strip() if newlines[-1].strip() else li.strip()

    newlines = [nl.strip() for nl in newlines]

    # If the total length is less than 99 minutes, we remove the hour mark
    if remove_hour_prefix and newlines and newlines[-1].startswith("00:"):
        newlines = [nl[3:] if nl.startswith("00:") else nl for nl in newlines]

    content = "\n".join(newlines)
    return content


def convert_verbose_json_to_timestamped_text(transcript: dict) -> str:
    # turn the json into vtt, then reuse the code used for youtube chapters
    buffer = ""
    for seg in transcript["segments"]:
        start = seconds_to_timecode(seg["start"])
        end = seconds_to_timecode(seg["end"])
        text = seg["text"]
        buffer += f"\n\n{start}.0 --> {end}\n{text}"

    buffer = buffer.strip()

    content = process_vtt_content_for_llm(buffer, remove_hour_prefix=False)
    return content


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_epub(
    path: Union[str, Path],
    file_hash: str,
) -> List[Document]:
    path = Path(path)
    assert path.exists(), f"file not found: '{path}'"
    loader = UnstructuredEPubLoader(path)
    content = loader.load()

    docs = [
        Document(
            page_content=content,
            metadata={},
        )
    ]
    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_powerpoint(
    path: Union[str, Path],
    file_hash: str,
) -> List[Document]:
    path = Path(path)
    assert path.exists(), f"file not found: '{path}'"
    loader = UnstructuredPowerPointLoader(path)
    content = loader.load()

    docs = [
        Document(
            page_content=content,
            metadata={},
        )
    ]
    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_word_document(
    path: Union[str, Path],
    file_hash: str,
) -> List[Document]:
    path = Path(path)
    assert path.exists(), f"file not found: '{path}'"
    try:
        loader = Docx2txtLoader(path)
        content = loader.load()
        if isinstance(content, str):
            docs = [Document(page_content=content)]
        else:
            assert isinstance(content, List) and all(
                isinstance(c, Document) for c in content
            ), f"unexpected type of content: {str(content)[:1000]}"
            docs = content
        check_docs_tkn_length(docs, path)
    except Exception as err:
        logger.warning(
            f"Error when loading word document with docx2txt, trying with unstructured: '{err}'"
        )
        loader = UnstructuredWordDocumentLoader(path)
        content2 = loader.load()
        docs = [Document(page_content=content2)]
        if isinstance(content2, str):
            docs = [Document(page_content=content2)]
        else:
            assert isinstance(content2, List) and all(
                isinstance(c, Document) for c in content2
            ), f"unexpected type of content: {str(content2)[:1000]}"
            docs = content2
        check_docs_tkn_length(docs, path)

    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_json_dict(
    path: Union[str, Path],
    json_dict_template: str,
    file_hash: str,
    metadata: Optional[Union[str, dict]] = None,
    json_dict_exclude_keys: Optional[List[str]] = None,
) -> List[Document]:
    path = Path(path)
    assert path.exists(), f"file not found: '{path}'"

    assert "{key}" in json_dict_template, "json_dict_template must contain '{key}'"
    assert "{value}" in json_dict_template, "json_dict_template must contain '{value}'"

    with Path(path).open("r") as f:
        d = json.load(f)
    assert d, "dict is empty"

    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    if not metadata:
        metadata = {}
    if json_dict_exclude_keys is None:
        json_dict_exclude_keys = []

    docs = []
    for k, v in d.items():
        if k in json_dict_exclude_keys:
            continue
        doc = Document(
            page_content=json_dict_template.replace("{key}", k).replace("{value}", v),
            metadata=metadata,
        )
        docs.append(doc)
    assert docs, "No document found in json_dict"

    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache
def load_url(path: str, title=None) -> List[Document]:
    logger.info(f"Loading url: '{path}'")

    # even if loading fails the title might be found so trying to keep
    # the first working title across trials
    if title == "Untitled":
        title = None

    loaded_success = False
    if not loaded_success:
        try:
            loader = WebBaseLoader("https://r.jina.ai/" + path, raise_for_status=True)
            text = "\n".join([doc.page_content for doc in loader.load()]).strip()
            assert text, "Empty text"
            if not title:
                if text.splitlines()[0].startswith("Title: "):
                    title = text.splitlines()[0].replace("Title: ", "", 1)
            text = text.split("Markdown Content:", 1)[1]
            text = markdownlinkparser_regex.sub(r"\1", text)  # remove links
            # remove markdown images for now as caption is disabled so it's just base64 or something like that, keep only a shorten image name
            text = markdownimage_regex.sub(md_shorten_image_name, text)
            docs = [
                Document(
                    page_content=text,
                    metadata={
                        "parser": "jinareader",
                    },
                )
            ]
            if title:
                for doc in docs:
                    doc.metadata["title"] = title
            check_docs_tkn_length(docs, path)
            loaded_success = True
        except Exception as err:
            logger.warning(f"Exception when using jina reader to parse url: '{err}'")

    if not loaded_success:
        try:
            loader = PlaywrightURLLoader(
                urls=[path], remove_selectors=["header", "footer"]
            )
            docs = loader.load()
            assert docs, "Empty docs when using playwright"
            if not title and "title" in docs[0].metadata:
                title = docs[0].metadata["title"]
            check_docs_tkn_length(docs, path)
            loaded_success = True
        except Exception as err:
            logger.warning(f"Exception when using playwright to parse url: '{err}'")

    if not loaded_success:
        try:
            loader = SeleniumURLLoader(urls=[path], browser="firefox")
            docs = loader.load()
            assert docs, "Empty docs when using selenium firefox"
            if (
                not title
                and "title" in docs[0].metadata
                and docs[0].metadata["title"] != "No title found."
            ):
                title = docs[0].metadata["title"]
            check_docs_tkn_length(docs, path)
            loaded_success = True
        except Exception as err:
            logger.warning(
                f"Exception when using selenium firefox to parse url: '{err}'"
            )

    if not loaded_success:
        try:
            loader = SeleniumURLLoader(urls=[path], browser="chrome")
            docs = loader.load()
            assert docs, "Empty docs when using selenium chrome"
            if (
                not title
                and "title" in docs[0].metadata
                and docs[0].metadata["title"] != "No title found."
            ):
                title = docs[0].metadata["title"]
            check_docs_tkn_length(docs, path)
            loaded_success = True
        except Exception as err:
            logger.warning(
                f"Exception when using selenium chrome to parse url: '{err}'\nUsing goose as fallback"
            )

    if not loaded_success:
        try:
            g = goose3.Goose()
            article = g.extract(url=path)
            text = article.cleaned_text
            docs = [Document(page_content=text)]
            assert docs, "Empty docs when using goose"
            if not title:
                if "title" in docs[0].metadata and docs[0].metadata["title"]:
                    title = docs[0].metadata["title"]
                elif article.title:
                    title = article.title
            check_docs_tkn_length(docs, path)
            loaded_success = True
        except Exception as err:
            logger.warning(f"Exception when using goose to parse url: '{err}'")

    if not loaded_success:
        try:
            loader = UnstructuredURLLoader([path])
            docs = loader.load()
            assert docs, "Empty docs when using UnstructuredURLLoader"
            if not title and "title" in docs[0].metadata and docs[0].metadata["title"]:
                title = docs[0].metadata["title"]
            check_docs_tkn_length(docs, path)
            loaded_success = True
        except Exception as err:
            logger.warning(
                f"Exception when using UnstructuredURLLoader to parse url: '{err}'"
            )

    if not loaded_success:
        try:
            loader = WebBaseLoader(path, raise_for_status=True)
            docs = loader.load()
            assert docs, "Empty docs when using html"
            if not title and "title" in docs[0].metadata and docs[0].metadata["title"]:
                title = docs[0].metadata["title"]
            check_docs_tkn_length(docs, path)
            loaded_success = True
        except Exception as err:
            logger.warning(
                f"Exception when using html as LAST RESORT to parse url: '{err}'"
            )

    # last resort, try to get the title from the most basic loader
    if not title:
        title = get_url_title(path)

    # store the title as metadata if missing
    if title:
        for d in docs:
            if "title" not in d.metadata or not d.metadata["title"]:
                d.metadata["title"] = title
            else:
                if d.metadata["title"] != title:
                    d.metadata["title"] = f"{title} - {d.metadata['title']}"

    return docs


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache
def load_youtube_playlist(playlist_url: str) -> Any:
    with youtube_dl.YoutubeDL({"quiet": False}) as ydl:
        try:
            loaded = ydl.extract_info(playlist_url, download=False)
        except (
            KeyError,
            youtube_dl.utils.DownloadError,
            youtube_dl.utils.ExtractorError,
        ) as e:
            raise Exception(
                logger.warning(
                    f"ERROR: Youtube playlist link skipped because : error during information \
        extraction from {playlist_url} : {e}"
                )
            )
    return loaded


@doc_loaders_cache.cache
def cached_yt_loader(
    path: str, add_video_info: bool, language: List[str], translation: Optional[str]
) -> List[Document]:
    logger.debug(f"Not using cache for youtube {path}")

    options = {
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": language,
        "skip_download": True,
        "subtitlesformat": "vtt",
        "allsubtitles": True,
        "extract_flat": False,
    }
    if translation is None:
        translation = []
    else:
        translation = [translation]

    with youtube_dl.YoutubeDL(options) as ydl:
        # First check available subs
        info = ydl.extract_info(path, download=False)

        title = info.get("fulltitle", None)

        # Check both manual and auto subs
        good_subs = info.get("subtitles", {})
        auto_subs = info.get("automatic_captions", {})

        if not good_subs and not auto_subs:
            raise Exception(
                f"No subtitles found for youtube video entitled '{title}' at link '{path}'"
            )

        sub = None
        for subs in [good_subs, auto_subs]:
            if sub is not None:
                break
            for lang in language + translation:
                if lang in subs.keys():
                    sub_url = [s for s in subs[lang] if s["ext"] == "vtt"][0]["url"]
                    sub = requests.get(sub_url).content
                    sub = ftfy.fix_text(sub.decode()).strip()
                    if not sub:
                        continue
                    break
        if not sub:
            available = list(set(list(good_subs.keys()) + list(auto_subs.keys())))
            raise Exception(
                f"Subtitles found but not for the languages '{language}' nor '{translation}' for youtube video entitled '{title}' at link '{path}'\nAvailable languages were: '{available}'"
            )

    # get metadata too
    meta = {"title": title, "author": info["channel"]}
    for k in [
        "description",
        "categories",
        "tags",
        "channel",
        "upload_date",
        "duration_string",
        "language",
    ]:
        if k in info and info[k]:
            meta["yt_" + k] = info[k]

    # the chapters, if present, are in seconds, while the vtt uses human readable timecodes so converting the chapters
    if "chapters" in info and info["chapters"]:
        chap = info["chapters"]

        for ich, ch in enumerate(chap):
            chap[ich]["start"] = seconds_to_timecode(chap[ich]["start_time"])
            chap[ich]["end"] = seconds_to_timecode(chap[ich]["end_time"])
            del chap[ich]["start_time"], chap[ich]["end_time"]

        meta["yt_chapters"] = json.dumps(chap, ensure_ascii=False)

    assert sub, "The found subtitles are empty. Try running that command again."

    content = process_vtt_content_for_llm(sub, remove_hour_prefix=True)

    docs = [
        Document(
            page_content=content,
            metadata=meta,
        )
    ]

    return docs


@doc_loaders_cache.cache(ignore=["path"])
def _pdf_loader(loader_name: str, path: str, file_hash: str) -> List[Document]:
    loader = pdf_loaders[loader_name](path)
    docs = loader.load()
    assert isinstance(docs, list), f"Output of {loader_name} is of type {type(docs)}"
    assert all(
        isinstance(d, Document) for d in docs
    ), f"Output of {loader_name} contains elements that are not Documents: {[type(c) for c in docs]}"
    return docs


@debug_return_empty
@optional_strip_unexp_args
def load_pdf(
    path: Union[str, Path],
    text_splitter: TextSplitter,
    file_hash: str,
    pdf_parsers: Union[str, List[str]] = "pymupdf",
    doccheck_min_lang_prob: float = min_lang_prob,
    doccheck_min_token: int = min_token,
    doccheck_max_token: int = max_token,
) -> List[Document]:
    path = Path(path)
    logger.info(f"Loading pdf: '{path}'")
    assert path.exists(), f"file not found: '{path}'"
    name = path.name
    if len(name) > 30:
        name = name[:15] + "..." + name[-15:]

    if isinstance(pdf_parsers, str):
        pdf_parsers = pdf_parsers.strip().split(",")
    assert pdf_parsers, "No pdf_parsers found"
    assert len(pdf_parsers) == len(
        set(pdf_parsers)
    ), f"You pdf_parsers list contains non unique elements. List: {pdf_parsers}"
    for pdfp in pdf_parsers:
        assert (
            pdfp in pdf_loaders
        ), f"The PDF loader '{pdfp}' was not present in the pdf_loaders keys. Your 'pdf_parsers' argument seems wrong."

    loaded_docs = {}
    # using language detection to keep the parsing with the highest lang
    # probability
    probs = {}
    passed_errs = []
    warned_errs = []

    info = "magic not run"
    try:
        import magic

        info = str(magic.from_file(path))
    except Exception as err:
        logger.warning(f"Failed to run python-magic: '{err}'")
    if "pdf" not in info.lower():
        logger.debug(
            f"WARNING: magic says that your PDF is not a PDF:\npath={path}\nMagic info='{info}'"
        )

    pbar = tqdm(
        total=len(pdf_parsers),
        desc=f"Parsing PDF {name}",
        unit="loader",
        disable=is_out_piped,
    )
    for loader_name in pdf_parsers:
        pbar.desc = f"Parsing PDF {name} with {loader_name}"
        try:
            if env.WDOC_DEBUG:
                logger.warning(f"Trying to parse {path} using {loader_name}")

            if pdf_loader_max_timeout > 0:
                with signal_timeout(
                    timeout=pdf_loader_max_timeout,
                    exception=TimeoutPdfLoaderError,
                ):
                    docs = _pdf_loader(loader_name, str(path), file_hash)
                try:
                    signal.alarm(0)  # disable alarm again just in case
                except Exception:
                    pass
            else:
                docs = _pdf_loader(loader_name, path, file_hash)

            pbar.update(1)

            for i, d in enumerate(docs):
                try:
                    pc = ftfy.fix_text(d.page_content)
                    docs[i].page_content = pc
                    # stupid pydantic error
                except Exception as err:
                    if "'dict' object has no attribute 'add'" in str(err):
                        pass
                    else:
                        raise
                if "pdf_loader_name" not in docs[i].metadata:
                    docs[i].metadata["pdf_loader_name"] = loader_name

            prob = check_docs_tkn_length(
                docs=docs,
                identifier=path,
                check_language=True,
                min_lang_prob=doccheck_min_lang_prob,
                min_token=doccheck_min_token,
                max_token=doccheck_max_token,
            )

            if prob >= 0.5:
                # only consider it okay if decent quality
                probs[loader_name] = prob
                loaded_docs[loader_name] = docs
                if prob > 0.95:
                    # select this one as its bound to be okay
                    logger.info(
                        f"Early stopping of PDF parsing because {loader_name} has prob {prob} for {path}"
                    )
                    break
            else:
                logger.info(
                    f"Ignore parsing by {loader_name} of '{path}' as it seems of poor quality: prob={prob}"
                )
                continue

            if len(probs.keys()) >= 3:
                # if more than 3 worked, take the best among them to save
                # time on running all the others
                break
        except Exception as err:
            if pdf_loader_max_timeout > 0:
                try:
                    signal.alarm(0)  # disable alarm again just in case
                except Exception:
                    pass
            if "content" not in locals():
                pbar.update(1)
            logger.debug(
                f"Error when parsing '{path}' with {loader_name}: {err}\nMagic info='{info}'"
            )

            if (
                str(err) in passed_errs
                and str(err) not in warned_errs
                and "token" not in str(err)
            ):
                exc_type, exc_obj, exc_tb = sys.exc_info()
                formatted_tb = "\n".join(
                    [str(li).strip() for li in traceback.format_tb(exc_tb)]
                )
                logger.warning(
                    f"The same error happens to multiple pdf loader, something is fishy.\nFull traceback:\n{formatted_tb}"
                )
                warned_errs.append(str(err))
            passed_errs.append(str(err))

    pbar.close()
    assert probs.keys(), f"No pdf parser succeeded to parse {path}"

    # no loader worked, exiting
    if not loaded_docs:
        raise Exception(f"No pdf parser worked for {path}")

    max_prob = max([v for v in probs.values()])

    if env.WDOC_DEBUG:
        logger.debug(f"Language probability after parsing {path}: {probs}")

    return loaded_docs[[name for name in probs if probs[name] == max_prob][0]]


def find_online_media(
    url: str,
    online_media_url_regex: Optional[str] = None,
    online_media_resourcetype_regex: Optional[str] = None,
    headless: bool = True,
) -> dict:

    def check_browser_installation(browser_type: str, crash: bool = False) -> bool:
        try:
            with playwright.sync_api.sync_playwright() as p:
                browser = getattr(p, browser_type).launch()
                browser.close()
            return True
        except Exception as err:
            if crash:
                raise
            if "p" in locals():
                logger.warning(str(p))
            logger.warning(str(err))
            return False

    # the media request will be stored in this dict
    video_urls = {
        "url_regex": [],
        "resourcetype_regex": [],
        "media": [],
        "mpeg": [],
        "mp4": [],
        "mp3": [],
        "m3u": [],
    }
    if online_media_url_regex:
        online_media_url_regex = re.compile(online_media_url_regex)
    if online_media_resourcetype_regex:
        online_media_resourcetype_regex = re.compile(online_media_resourcetype_regex)
    nonmedia_urls = []

    def request_filter(req) -> None:
        if online_media_url_regex is not None and online_media_url_regex.match(req.url):
            video_urls["url_regex"].append(req.url)
        elif (
            online_media_resourcetype_regex is not None
            and online_media_resourcetype_regex.match(req.resource_type)
        ):
            video_urls["resourcetype_regex"].append(req.url)
        elif req.resource_type == "media":
            video_urls["media"].append(req.url)
        elif "media" in req.resource_type:
            video_urls["media"].append(req.url)
        elif "mpeg" in req.resource_type:
            video_urls["mpeg"].append(req.url)
        elif "m3u" in req.resource_type or ".m3u" in req.url:
            video_urls["m3u"].append(req.url)
        elif "mp3" in req.resource_type or ".mp3" in req.url:
            video_urls["mp3"].append(req.url)
        elif "mp4" in req.resource_type or ".mp4" in req.url:
            video_urls["mp4"].append(req.url)
        else:
            nonmedia_urls.append(req.url)

    if check_browser_installation("firefox"):
        installed = "firefox"
    elif check_browser_installation("chromium"):
        installed = "chromium"
    else:
        logger.warning(
            "Couldn't launch either firefox or chromium using playwright. "
            "Maybe try running 'playwright install'? Retrying to load them on "
            "purpose to make us crash and display the actual error."
        )
        check_browser_installation("firefox", crash=True)
        check_browser_installation("chromium", crash=True)
        raise Exception("We should have crashed earlier?!")

    with playwright.sync_api.sync_playwright() as p:
        browser = getattr(p, installed).launch(headless=headless)

        context = browser.new_context(
            java_script_enabled=True,
            geolocation={
                "latitude": 38.8954381,
                "longitude": -77.0312812,
            },
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            ignore_https_errors=True,
        )
        page = context.new_page()

        # start logging requests
        page.on("request", lambda request: request_filter(request))
        browser.on("request", lambda request: request_filter(request))
        context.on("request", lambda request: request_filter(request))

        # load page
        page.goto(url)
        try:
            page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.debug(
                f"Ignoring exception on wait_for_load_state('networkidle'): {e}"
            )

        # Scroll the page to trigger lazy-loaded content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)  # Wait for X seconds after scrolling
        page.evaluate("window.scrollTo(0, 0)")

        # Try to click on video play buttons using various selectors
        play_button_selectors = [
            '[class*="play-button"]',
            '[class*="play_button"]',
            '[class*="playbutton"]',
            '[class*="playback"]',
            '[class*="play-back"]',
            '[class*="play_back"]',
            '[class*="play"]',
            '[aria-label="Play"]',
            ".ytp-play-button",
            ".play-button",
            '[aria-label="播放"]',
            "div.avp-icon.avp-icon-playback",
        ]
        for selector in play_button_selectors:
            try:
                # Try clicking directly first (for specific selectors)
                page.click(selector, timeout=200)
                logger.debug(f"Clicked element matching selector: {selector}")
                page.wait_for_timeout(1000)  # Wait after click
                continue  # Move to next selector if successful
            except Exception:
                # If direct click fails or selector is general (like class*), try querying all
                try:
                    playback_elements = page.query_selector_all(selector)
                    for element in playback_elements:
                        if not element.is_visible() or not element.is_enabled():
                            continue
                        logger.debug(f"Found clickable element via query: {element}")
                        try:
                            element.click(timeout=500)
                            logger.debug(
                                f"Clicked element: {element.evaluate('el => el.outerHTML')}"
                            )
                            page.wait_for_timeout(1000)  # Wait after click
                            # Don't break here, maybe multiple elements match a general selector
                        except Exception as click_err:
                            logger.debug(
                                f"Failed to click element {element}: {click_err}"
                            )
                except Exception as query_err:
                    logger.debug(
                        f"Failed to query or click elements for selector {selector}: {query_err}"
                    )

        if not any(v for v in video_urls.values()):
            # Wait a bit more for any video to start loading if no media URLs found yet
            page.wait_for_timeout(10000)

        browser.close()

    # deduplicate urls
    for k, v in video_urls.items():
        video_urls[k] = list(set(v))

    return video_urls


@debug_return_empty
@optional_strip_unexp_args
@doc_loaders_cache.cache(ignore=["path"])
def load_online_media(
    path: str,
    audio_backend: Literal["whisper", "deepgram"],
    loaders_temp_dir: Path,
    audio_unsilence: bool = True,
    whisper_lang: Optional[str] = None,
    whisper_prompt: Optional[str] = None,
    deepgram_kwargs: Optional[dict] = None,
    online_media_url_regex: Optional[str] = None,
    online_media_resourcetype_regex: Optional[str] = None,
) -> List[Document]:

    urls_to_try = [path]
    extra_media = find_online_media(
        url=path,
        online_media_url_regex=online_media_url_regex,
        online_media_resourcetype_regex=online_media_resourcetype_regex,
    )
    for k in [
        "url_regex",
        "resourcetype_regex",
        "media",
        "mpeg",
        "mp4",
        "mp3",
        "m3u",
    ]:
        urls_to_try.extend(extra_media[k])
    urls_to_try = list(set(urls_to_try))
    logger.info(f"Found {len(urls_to_try)} urls to try to get the media:")
    for u in urls_to_try:
        logger.info(f"  - {u}")

    def dl_audio_from_url(trial: int, url: str) -> Path:
        file_name = (
            loaders_temp_dir / f"online_media_{uuid6.uuid6()}"
        )  # without extension!
        ydl_opts = {
            # 'format': 'bestaudio/best',
            "format": "bestaudio/best",
            # 'force_generic_extractor': True,
            # 'default_search': 'auto',
            # 'match_filter': lambda x: None,
            "hls_prefer_native": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            # with extension
            "outtmpl": f"{file_name.absolute().resolve()}.%(ext)s",
            "verbose": env.WDOC_VERBOSE,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        candidate = []
        for f in loaders_temp_dir.iterdir():
            if file_name.name in f.name:
                candidate.append(f)
        assert len(candidate), f"Audio file of {url} failed to download?"
        assert (
            len(candidate) == 1
        ), f"Multiple audio file found for video: '{candidate}'"
        audio_file = candidate[0].absolute()
        return audio_file

    audio_file = None
    good_url = None
    for iurl, url in enumerate(urls_to_try):
        try:
            audio_file = dl_audio_from_url(trial=iurl, url=url)
            good_url = url
            break
        except Exception as err:
            logger.warning(
                f"Failed #{iurl+1}/{len(urls_to_try)} to download a media from url '{url}': '{err}'"
            )

    assert audio_file is not None, f"Failed to find suitable media for url '{path}'"

    audio_hash = file_hasher({"path": str(Path(audio_file).absolute())})
    audio_path = loaders_temp_dir / f"audio_from_video_{uuid6.uuid6()}.mp3"
    assert not audio_path.exists()

    # extract audio from video (sometimes instead of just the audio the whole video is downloaded)
    try:
        logger.info(
            f"Exporting audio from {audio_file} to {audio_path} (this can take some time)"
        )
        t = time.time()
        ffmpeg.input(
            audio_file,
        ).output(str(audio_path.resolve().absolute())).run()
        logger.info(f"Done extracting audio in {time.time()-t:.2f}s")
    except Exception as err:
        logger.warning(
            f"Error when getting audio from video using ffmpeg. Retrying with pydub. Error: '{err}'"
        )

        try:
            logger.debug(f"Audio path: '{audio_path}'")
            # don't delete it as some users might need it
            # Path(audio_path).unlink(missing_ok=True)
            audio = pydub.AudioSegment.from_file(audio_file)
            # extract audio from video
            logger.info(
                f"Extracting audio from {audio_file} to {audio_path} (this can take some time)"
            )
            t = time.time()
            audio.export(audio_path, format="mp3")
            logger.info(f"Done extracting audio in {time.time()-t:.2f}s")
        except Exception as err:
            raise Exception(
                f"Error when getting audio from video using ffmpeg: '{err}'"
            )

    assert Path(audio_path).exists(), f"FileNotFound: {audio_path}"

    # now need the hash from the mp3, not video
    audio_hash = file_hasher({"path": audio_path})

    sub_loaders_temp_dir = loaders_temp_dir / "local_audio"
    sub_loaders_temp_dir.mkdir()
    parsed_audio = load_local_audio(
        path=audio_path,
        loaders_temp_dir=sub_loaders_temp_dir,
        file_hash=audio_hash,
        audio_backend=audio_backend,
        whisper_lang=whisper_lang,
        whisper_prompt=whisper_prompt,
        deepgram_kwargs=deepgram_kwargs,
        audio_unsilence=audio_unsilence,
    )

    for ipa, pa in enumerate(parsed_audio):
        parsed_audio[ipa].metadata["online_media_url"] = str(good_url)

    return parsed_audio


# Validation: Check that all loader functions exist
def _validate_loader_functions():
    """Validate that all loader functions referenced in FILETYPE_TO_LOADER exist."""
    current_module = sys.modules[__name__]
    for filetype, func_name in FILETYPE_TO_LOADER.items():
        if not hasattr(current_module, func_name):
            raise Exception(
                f"Loader function '{func_name}' for filetype '{filetype}' not found in module"
            )


# Run validation when module is imported
_validate_loader_functions()
