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
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path

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
def test_get_element_rect_returns_wrong_dimensions_when_element_is_rotated(driver):
    """
    This test reproduces the bug where getRect returns the unrotated element dimensions.
    It navigates to a page with a 200x200 element rotated by -45 degrees. The expected
    bounding box should be approximately 282x282. The test will fail if the returned
    dimensions are 200x200.
    """
    html_file = Path(__file__).parent.joinpath("rotated.html")
    driver.get(f"file://{html_file.absolute()}")
    
    rotated_element = driver.find_element(By.ID, "rotated")
    rect = rotated_element.rect
    
    # The original size is 200x200. When rotated by 45 degrees, the bounding box
    # becomes a square with side length sqrt(200^2 + 200^2) = 282.84
    expected_size = 282.84
    
    # The test is expected to fail here, as ChromeDriver returns 200 instead of 282.
    assert rect["width"] == pytest.approx(expected_size, abs=1)
    assert rect["height"] == pytest.approx(expected_size, abs=1)
