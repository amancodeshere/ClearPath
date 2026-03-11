import re
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def remove_urls(text: str) -> str:
    """
    'Service delayed see https://t.co/abc' -> 'Service delayed see'
    """
    url_pattern = r"http\S+|www\S+"
    return re.sub(url_pattern, "", text)


def remove_mentions(text: str) -> str:
    """
    Removes Twitter mentions such as @T1SydneyTrains.
    """
    mention_pattern = r"@\w+"
    return re.sub(mention_pattern, "", text)


def process_hashtags(text: str) -> str:
    """
    Converts hashtags into plain words.
        '#flooding on tracks' -> 'flooding on tracks'
    """
    hashtag_pattern = r"#(\w+)"
    return re.sub(hashtag_pattern, r"\1", text)


def remove_emojis(text: str) -> str:
    """
    Removes emojis and non-ASCII characters.
        '"⚠️❌" services cancelled' -> ' services cancelled'
    """
    return text.encode("ascii", "ignore").decode()


def remove_punctuation(text: str) -> str:
    """
    Removes punctuation characters while preserving spaces.
    """
    punctuation_pattern = r"[^\w\s]"
    return re.sub(punctuation_pattern, " ", text)


def normalise_whitespace(text: str) -> str:
    """
    Collapses multiple spaces into a single space.
    """
    return re.sub(r"\s+", " ", text).strip()


def normalise_text(text: str) -> str:
    """
    This function applies all cleaning steps in sequence
    to produce a clean string suitable for model inference.

    Processing steps:
        1. Lowercase
        2. Remove URLs
        3. Remove mentions
        4. Convert hashtags to words
        5. Remove emojis
        6. Remove punctuation
        7. Normalise whitespace

    @:param text : str -> Raw tweet text
    @:returns str -> Normalised tweet text
    """

    if not text:
        return ""

    try:
        text = text.lower()

        text = remove_urls(text)
        text = remove_mentions(text)
        text = process_hashtags(text)
        text = remove_emojis(text)
        text = remove_punctuation(text)

        text = normalise_whitespace(text)

        return text

    except Exception as e:
        logger.error(f"Text normalisation failed: {e}")
        return text

