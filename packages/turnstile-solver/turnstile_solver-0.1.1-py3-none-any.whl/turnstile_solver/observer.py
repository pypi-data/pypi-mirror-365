"""
Internal module to monitor Cloudflare Turnstile verification state.

This class uses JavaScript MutationObserver to detect whether the Turnstile
has been solved, based on widget type: embedded checkbox or full-page challenge.
"""

from typing import Literal


# Shared script IDs across all instances.
# Ensures each observer script is injected only once.
# Any instance can inject, reuse, or remove the script.
SCRIPT_IDS = {"challenge": None, "embedded": None}

class TurnstileObserver:
    """
    Monitors the Turnstile widget and detects when it has been verified.
    Works for both 'embedded' and 'challenge' types by injecting JS observers.
    """


    def __init__(self, driver):
        """
        :param driver: Selenium WebDriver instance.
        :param timeout: Time (in seconds) after which the observer auto-disconnects.
        """
        self.driver = driver

    def _observe_embedded(self, timeout) -> None:
        """
        Injects JS to observe attribute changes on the embedded Turnstile <input>.
        If any attribute changes, verification is considered successful.
        """
        js = f"""
            const widgetTimeout = {timeout};
            const widgetStartTime = Date.now();

            if (window.top === window.self) {{
                function observeWidget() {{
                    if ((Date.now() - widgetStartTime) / 1000 >= widgetTimeout) return;

                    const widget = document.querySelector(".cf-turnstile[data-sitekey]");
                    if (!widget) return setTimeout(observeWidget, 1000);

                    const input = widget.querySelector("input");
                    if (!input) return setTimeout(observeWidget, 1000);

                    const observer = new MutationObserver(() => {{
                        localStorage.setItem("turnstile_verified", "true");
                        observer.disconnect();
                    }});
                    observer.observe(input, {{ attributes: true }});

                    setTimeout(() => observer.disconnect(), widgetTimeout * 1000);
                }}
                observeWidget();
            }}
        """

        # Run it on future navigation
        res = self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
        SCRIPT_IDS["embedded"] = res["identifier"]

        # Run it on current page also
        self.driver.execute_cdp_cmd("Runtime.evaluate", {"expression": js})

    def _observe_challenge(self, timeout) -> None:
        """
        Injects JS to observe visibility of challenge success text.
        If it becomes visible, verification is considered successful.
        """
        js = f"""
            const challengeTimeout = {timeout};
            const challengeStartTime = Date.now();

            if (window.top === window.self) {{
                function observeChallenge() {{
                    if ((Date.now() - challengeStartTime) / 1000 >= challengeTimeout) return;

                    const target = document.querySelector("#challenge-success-text");
                    if (!target || !target.parentElement) return setTimeout(observeChallenge, 1000);

                    function check() {{
                        if (target.getClientRects().length > 0) {{
                            localStorage.setItem("turnstile_verified", "true");
                            observer.disconnect();
                        }}
                    }}

                    const observer = new MutationObserver(check);
                    observer.observe(target.parentElement, {{
                        childList: true,
                        attributes: true,
                        characterData: true,
                        subtree: false
                    }});

                    check(); // Initial check
                    setTimeout(() => observer.disconnect(), challengeTimeout * 1000);
                }}

                observeChallenge();
            }}
        """

        # Run it on future navigation
        res = self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
        SCRIPT_IDS["challenge"] = res["identifier"]

        # Run it on current page also
        self.driver.execute_cdp_cmd("Runtime.evaluate", {"expression": js})

    def start(self, cf_type: Literal["challenge", "embedded"], timeout:int) -> None:
        """
        Start observing the page for Turnstile verification state.

        :param cf_type: Turnstile type - 'embedded' or 'challenge'.
        """
        if not isinstance(timeout, (int, float)):
            raise ValueError("Invalid parameter: 'timeout' must be an int or float (in seconds)")

        if cf_type == "embedded":
            if not SCRIPT_IDS[cf_type]:
                self._observe_embedded(timeout)

        elif cf_type == "challenge":
            if not SCRIPT_IDS[cf_type]:
                self._observe_challenge(timeout)

        else:
            raise ValueError("cf_type must be 'embedded' or 'challenge'.")

    def is_verified(self) -> bool:
        """
        Check if Turnstile has been verified. Uses a flag in localStorage.

        :return: True if verified, False otherwise.
        """
        result = self.driver.execute_cdp_cmd("Runtime.evaluate", {
            "expression": """
                (function() {
                    const val = localStorage.getItem("turnstile_verified");
                    if (val) localStorage.removeItem("turnstile_verified");
                    return val;
                })()
            """,
            "returnByValue": True
        })["result"]["value"]

        return result == "true"

    def remove(self) -> None:
        """
        Remove the injected JS observer from future navigation.
        """
        for key, script_id in SCRIPT_IDS.items():
            if script_id:
                self.driver.execute_cdp_cmd("Page.removeScriptToEvaluateOnNewDocument", {
                    "identifier": script_id,
                })
                SCRIPT_IDS[key] = None
