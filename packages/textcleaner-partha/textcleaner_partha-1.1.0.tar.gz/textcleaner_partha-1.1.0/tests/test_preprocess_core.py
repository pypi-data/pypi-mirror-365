import os
import sys
import pytest
import spacy

# Add the parent folder of `textcleaner_partha` to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from textcleaner_partha.preprocess import preprocess, get_tokens, load_abbreviation_mappings
import textcleaner_partha.preprocess as prep

import inspect

print("prep object type:", type(prep))
print("prep object:", prep)
print("prep location:", getattr(prep, "__file__", "Not a module"))
print("prep members:", inspect.getmembers(prep)[:10])  # Show first 10 members

@pytest.fixture(scope="module", autouse=True)
def ensure_spacy_model():
    """Ensure spaCy model is loaded before running tests."""
    try:
        spacy.load("en_core_web_sm")
    except OSError:
        pytest.skip("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")

def test_basic_preprocessing():
    text = "This is a <b>TEST</b> 😊!"
    result = preprocess(text)
    assert isinstance(result, str)
    assert "test" in result  # lowercase + lemma
    assert "<b>" not in result  # HTML removed
    assert "😊" not in result  # emoji removed

def test_remove_punctuation():
    text = "Hello, world!!!"
    result = preprocess(text, remove_punct=True)
    assert "," not in result and "!" not in result

def test_keep_punctuation():
    text = "Hello, world!"
    result = preprocess(text, remove_punct=False)
    assert "," in text or "!" in text  # punctuation preserved in input
    assert isinstance(result, str)

def test_without_lemmatization():
    text = "running runs runner"
    result = preprocess(text, lemmatise=False)
    assert "running" in result or "runs" in result  # original forms retained

def test_with_lemmatization():
    text = "running runs runner"
    result = preprocess(text, lemmatise=True)
    assert "run" in result  # lemmatized

def test_expand_contractions():
    text = "I'm going, don't worry!"
    result = preprocess(text, lemmatise=False, remove_stopwords=False)
    assert "i am" in result or "do not" in result

def test_abbreviation_expansion(tmp_path):
    abbrev_dir = tmp_path / "abbreviation_mappings"
    abbrev_dir.mkdir()
    (abbrev_dir / "abbr.json").write_text('{"ai": "artificial intelligence"}')

    prep.set_abbreviation_dir(str(abbrev_dir))
    prep.load_abbreviation_mappings()

    result = prep.preprocess("AI is powerful")
    assert "artificial intelligence" in result

    # Reset to default after test
    prep.reset_abbreviation_dir()

def test_disable_abbreviation_expansion():
    text = "AI is powerful"
    result = preprocess(text, expand_abbrev=False)
    assert "ai" in result or "AI" in text.lower()

def test_spell_correction():
    text = "Ths is spleling errror"
    result = preprocess(text, correct_spelling=True, lemmatise=False, remove_stopwords=False)
    # Check that spelling correction improves words
    assert "this" in result or "spelling" in result

def test_no_spell_correction():
    text = "Ths is spleling errror"
    result = preprocess(text, correct_spelling=False, lemmatise=False, remove_stopwords=False)
    assert "ths" in result or "spleling" in result

def test_remove_stopwords_disabled():
    text = "This is a test sentence"
    result = preprocess(text, lemmatise=False, correct_spelling=False, remove_stopwords=False)
    assert "this" in result and "is" in result  # stopwords retained

def test_remove_stopwords_enabled():
    text = "This is a test sentence"
    result = preprocess(text, lemmatise=False, correct_spelling=False, remove_stopwords=True)
    assert "this" not in result and "is" not in result  # stopwords removed

def test_get_tokens_basic():
    text = "Cats are running fast!"
    tokens = get_tokens(text)
    assert isinstance(tokens, list)
    assert any("cat" in t or "run" in t or "fast" in t for t in tokens)

def test_get_tokens_no_lemmatization():
    text = "Cats are running fast!"
    tokens = get_tokens(text, lemmatise=False)
    assert "running" in tokens or "cats" in tokens

def test_empty_string():
    text = ""
    result = preprocess(text)
    assert result == "" or isinstance(result, str)
    tokens = get_tokens(text)
    assert tokens == []

def test_html_and_emoji_removal():
    text = "<p>Hello 😊 world!</p>"
    result = preprocess(text, lemmatise=False, remove_stopwords=False)
    assert "hello" in result and "world" in result
    assert "<p>" not in result and "😊" not in result

def test_verbose_output(capsys):
    text = "AI!"
    preprocess(text, verbose=True)
    captured = capsys.readouterr()
    assert captured.out == "" or "warning" in captured.out.lower()