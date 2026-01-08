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
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
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
def test_issue_469831357_reproduction(driver):
    """
    This test reproduces crbug.com/469831357.
    """
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_469831357.html')
    file_url = f'file://{html_path}'

    driver.get(file_url)

    shadow_host = driver.find_element(By.ID, 'shadow-host')
    shadow_root = shadow_host.shadow_root
    iframe = shadow_root.find_element(By.CSS_SELECTOR, 'iframe')

    # Now, switch to the iframe context
    driver.switch_to.frame(iframe)

    # Attempt to find and click the button within the iframe
    button = driver.find_element(By.TAG_NAME, 'button')
    # This is the step that is expected to fail due to the bug.
    button.click()
