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
    browser_version = "118"

    options = Options()
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
    This test reproduces bug 42323703: Unable to take a screenshot after browser back/forward.

    Reproduction Steps:
    1. Navigate to an initial URL.
    2. Navigate to a second URL.
    3. Take a screenshot (this should succeed).
    4. Navigate back using driver.back().
    5. Attempt to take a screenshot (this is expected to fail with an unhandled inspector error).
    6. Navigate forward using driver.forward().
    7. Attempt to take a screenshot (this is also expected to fail with an unhandled inspector error).

    The test is expected to fail on the screenshot attempts after back() and forward()
    due to the bug. The assertion checks for the specific error message or
    the inability to save the screenshot.
    """
    driver.get("http://httpbin.org/anything?test1=123")
    driver.save_screenshot('image1.png')

    driver.back()
    try:
        driver.save_screenshot('image2.png')
    except Exception as e:
        assert "Unable to capture screenshot" in str(e)

    driver.forward()
    try:
        driver.save_screenshot('image3.png')
    except Exception as e:
        assert "Unable to capture screenshot" in str(e)

