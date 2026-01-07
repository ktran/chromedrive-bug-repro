#  Copyright 2025 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# The chrome and chromedriver installation can take some time.
# Give 5 minutes to install everything.
TIMEOUT = 5 * 60 * 1000


@pytest.fixture(scope="module")
def driver():
    # By default, the test uses the latest stable Chrome version.
    # Replace the "stable" with the specific browser version if needed,
    # e.g. 'canary', '115' or '144.0.7534.0' for example.
    browser_version = "stable"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.browser_version = browser_version

    service = Service(service_args=["--log-path=chromedriver.log", "--verbose"])

    driver = webdriver.Chrome(options=options, service=service)

    yield driver

    driver.quit()


@pytest.mark.timeout(TIMEOUT)
def test_should_be_able_to_navigate_to_google_com(driver):
    """This test is intended to verify the setup is correct."""
    driver.get("https://www.google.com")
    logging.info(driver.title)
    assert driver.title == "Google"


@pytest.mark.timeout(TIMEOUT)
def test_issue_reproduction(driver):
    """
    This test reproduces the ChromeDriver bug where `driver.current_url` returns an incoherent URL
    when navigating to an archived page on `web.archive.org`.

    Reproduction Steps:
    1. Navigate to an archived page on `web.archive.org`.
    2. Retrieve the `driver.current_url`.

    Expected Failure:
    The test asserts that `driver.current_url` should be the `archive.org` URL.
    However, due to the bug (crbug.com/42323616), `driver.current_url` returns the original
    website's URL (http://tilde.town/) instead of the expected `archive.org` URL.
    Therefore, this assertion is expected to fail if the bug exists.
    """
    expected_url = "https://web.archive.org/web/20231003135536/http://tilde.town/"
    driver.get(expected_url)
    logging.info(f"Current URL: {driver.current_url}")
    # The bug causes driver.current_url to be 'http://tilde.town/' instead of 'expected_url'
    assert driver.current_url == expected_url
