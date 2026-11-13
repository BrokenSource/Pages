from attrs import define
from playwright.sync_api import sync_playwright


@define
class Cover:

    def screenshot(self,
        url: str,
        width: int=3840,
        height: int=2160,
    ) -> bytes:
        with sync_playwright() as play:
            browser = play.firefox.launch(headless=True)
            page = browser.new_page(viewport={
                "width": width,
                "height": height,
            })

            page.goto(url, wait_until="networkidle")

            return page.screenshot(
                type="png",
                path=None,
            )
