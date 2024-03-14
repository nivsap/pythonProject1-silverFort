import re
import enchant
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter

# Initialize the webdriver
driver = None


@pytest.fixture(scope="session", autouse=True)
def setup():
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://en.wikipedia.org/wiki/Multi-factor_authentication")
    yield
    driver.quit()


def extract_text():
    # optimize : we can take the content of whole page and than extract the relevant text by regex!
    paragraphs = [
        ("Authentication takes place when someone tries to",
         "//p[contains(., 'Authentication takes place when someone tries to')]"),
        (
            "The use of multiple authentication factors",
            "//p[contains(., 'The use of multiple authentication factors')]"),
        ("Something the user has", "//ul[contains(., 'Something the user has')]"),
        ("An example of two-factor authentication", "//p[contains(., 'An example of two-factor authentication')]"),
        ("A third-party authenticator app enables two-factor authentication",
         "//p[contains(., 'A third-party authenticator app enables two-factor authentication')]")
    ]
    # we can use properties file or config.ini to improve hardcoded strings as above

    extracted_text = ""
    for section, locator in paragraphs:
        try:
            text = wait_for_element((By.XPATH, locator)).text
            extracted_text += f"{text} "
        except Exception as e:
            pytest.fail(f"Failed to perform search for term : {str(e)}")
            print(f"Failed to extract text for section '{section}': {str(e)}")
    print(extracted_text)
    return extracted_text


def count_unique_words(text):
    # Count unique words in the text
    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = Counter(words)
    print(word_counts)
    return word_counts


def check_typos(text):
    d = enchant.Dict("en_US")
    typos = [word for word in re.findall(r'\b\w+\b', text.lower()) if not d.check(word)]
    print(typos)
    return typos


# Helper function to wait for element visibility
def wait_for_element(by_locator, timeout=10):
    global driver
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(by_locator))
    except Exception as e:
        print(f"Element not found: {str(e)}")
        pytest.fail(f"Failed to perform search for term : {str(e)}")
        return None


# Test function to check text extraction
@pytest.mark.parametrize("section",
                         ["Authentication", "The use of multiple authentication factors", "Something the user has",
                          "An example of two-factor authentication",
                          "A third-party authenticator app enables two-factor authentication"])
def test_text_extraction(section):
    extracted_text = extract_text()
    assert section in extracted_text, f"Section '{section}' not found in extracted text."


# Test function to check unique word count
def test_unique_word_count():
    extracted_text = extract_text()
    unique_words = count_unique_words(extracted_text)
    assert len(unique_words) > 0, "No unique words found in extracted text."


# Test function to check typo detection
def test_typos():
    extracted_text = extract_text()
    typos = check_typos(extracted_text)
    assert len(typos) != 0, f"Typos not found in text: {typos}"


# Execute the tests and generate report
pytest.main(["-v", "--html=report.html"])
