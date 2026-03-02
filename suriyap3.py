from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
import google_sheets
import time

URLS = [
    "https://chartink.com/screener/copy-copy-copy-sreelakshmi-guruvayoorappan-b-atr-volume-rocket-8",
    "https://chartink.com/screener/agp-bullish2-p5",
    "https://chartink.com/screener/aaa13-vp-sheshapathi",
    "https://chartink.com/screener/agp-shesha-bulloong1",
    "https://chartink.com/screener/shesha-magic-buy-love",
    "https://chartink.com/screener/copy-mahi-2-master-trader-vishnu-final-40-address-this-urgent-bellinaire-38-to-47-3",
    "https://chartink.com/screener/agp-bullish2",
    "https://chartink.com/screener/copy-atp-above-long-24",
    "https://chartink.com/screener/22-nw-shesha-magic-buy-love-fut",
    "https://chartink.com/screener/copy-nr-f-0",
    "https://chartink.com/screener/copy-rk-position-f-0",
    "https://chartink.com/screener/copy-f-0-future",
    "https://chartink.com/screener/smbg2-new-multibegger-stocks-for-next-few-days",
    "https://chartink.com/screener/cash-tss-momentum-long",
    "https://chartink.com/screener/copy-atp-above-long-cash-2",
    "https://chartink.com/screener/copy-copy-future-and-options-2-1-4",
    "https://chartink.com/screener/copy-atp-above-long-fut1",
    "https://chartink.com/screener/copy-copy-daily-min-f-0-trade-2",
    "https://chartink.com/screener/copy-atr-volume-f-o-200-wkly-rsi-70-new",
    "https://chartink.com/screener/copy-multibagar-5",
    "https://chartink.com/screener/copy-the-best-btst-193",
    "https://chartink.com/screener/22-nw-shesha-magic-buy-love",
    "https://chartink.com/screener/copy-richie-rich-f-0-2",
    "https://chartink.com/screener/all-u1-nk-sir-s-uptrend-stocks-all-time-uptrend",
    "https://chartink.com/screener/copy-sjbl6ch-shesha-buy-bollinger-band-weekly",
    "https://chartink.com/screener/copy-copy-bb-blaster-2",
    "https://chartink.com/screener/copy-atr-volume-f-o-200-wkly-rsi-70-16"
    ]
       
sheet_id = "1bKrdupQL1LXAOXwmM1YsoN3xoGiMfS7pgzTkQFC3cjw"
worksheet_names = [
    "p1","p2","p3","p4","p5","p6","p7","p8","p9","p10",
    "p11","p12","p13","p14","p15","p16","p17","p18","p19","p20","p21","p22","p23","p24","p25","p26","p27"]

def scrape_chartink(url, worksheet_name):
    print(f"\n🚀 Starting scrape for '{worksheet_name}'")
    print(f"🌐 Loading URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        headers = ["Sr", "Stock Name", "Symbol", "Links", "Change", "Price", "Volume"]

        try:
            page.goto(url, wait_until="networkidle")
            time.sleep(3)

            if page.is_visible("text='No records found'"):
                print(f"⚠️ No records found at {url}. Writing blank row.")
                rows = [[""]]
            else:
                try:
                    '''
                    page.wait_for_selector("div.relative table tbody tr", timeout=60000)
                    table_rows = page.query_selector_all("div.relative table tbody tr")
                    '''
                    page.wait_for_selector("div.relative table tbody tr", timeout=60000)
                    table_rows = page.query_selector_all("div.relative table tbody tr")

                    print(f"📥 Extracted {len(table_rows)} rows.")

                    rows = []
                    for row in table_rows:
                        cells = row.query_selector_all("td")
                        row_data = [cell.inner_text().strip() for cell in cells]
                        rows.append(row_data)

                    if len(rows) == 0:
                        print("⚠️ Table present but no data rows. Writing blank row.")
                        rows = [[""]]

                except PlaywrightTimeoutError:
                    print(f"❌ Table not found at {url}. Writing blank row.")
                    rows = [[""]]

            google_sheets.update_google_sheet_by_name(
                sheet_id, worksheet_name, headers, rows
            )

        except PlaywrightTimeoutError:
            print(f"❌ Timeout error at {url}. Writing blank row.")
            google_sheets.update_google_sheet_by_name(
                sheet_id, worksheet_name, headers, [[""]]
            )

        except Exception as e:
            print(f"❌ Unexpected error: {e}. Writing blank row.")
            google_sheets.update_google_sheet_by_name(
                sheet_id, worksheet_name, headers, [[""]]
            )

        finally:
            page.screenshot(path=f"{worksheet_name}_debug.png", full_page=True)
            browser.close()

        now = datetime.now().strftime("Last updated on: %Y-%m-%d %H:%M:%S")
        google_sheets.append_footer(sheet_id, worksheet_name, [now])

        print(f"✅ Worksheet '{worksheet_name}' updated.")

for index, url in enumerate(URLS):
    scrape_chartink(url, worksheet_names[index])
    print(f"⏱️ Finished updating '{worksheet_names[index]}'")

