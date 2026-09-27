from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
import google_sheets
import time

URLS = [
    "https://chartink.com/screener/fut-sreelakshmi-guruvayoorappan-b-atr-volume-rocket",
    "https://chartink.com/screener/copy-copy-copy-future-and-option-pin-bar-pranshu-tiwari-2",
    "https://chartink.com/screener/50aaaagp-shesha-bearish-2",
    "https://chartink.com/screener/copy-copy-nks-future-trick-bb-part-2-21",
    "https://chartink.com/screener/copy-copy-nks-future-trick-bb-part-2-20",
    "https://chartink.com/screener/fut-hammar-cash-low-paradaily",
    "https://chartink.com/screener/copy-bullish-kicker-with-momentum-btst-futures-99",
    "https://chartink.com/screener/copy-bearish-kicker-with-momentum-stbt-futures-58",
    "https://chartink.com/screener/sncopy-shani-crow-future",
    "https://chartink.com/screener/copy-shani-crow-future-2",
    "https://chartink.com/screener/copy-copy-copy-copy-merge-nk-daily-convergence-future-nk-sir-hm-positional-buy-nk-sir-4796",
    "https://chartink.com/screener/tcssjbl1fut-rocket",
    "https://chartink.com/screener/copy-narayana-futures-positional-bearish-111",
    "https://chartink.com/screener/new-11111sjbl1fut-rocket",
    "https://chartink.com/screener/copy-love-future",
    "https://chartink.com/screener/tnsjbl5fut-bulloong-4",
    "https://chartink.com/screener/copy-sjbl5fut-bulloong-4",
    "https://chartink.com/screener/11111sjbl1fut-rocket",
    "https://chartink.com/screener/copy-sjbl1fut-rocket-2",
    "https://chartink.com/screener/50-the-best-btst",
    "https://chartink.com/screener/50shesha-magic-buy-love",
    "https://chartink.com/screener/50-oneeeeeee",
    "https://chartink.com/screener/50stocks-in-downtrend",
    "https://chartink.com/screener/copy-multibagar-5",
    "https://chartink.com/screener/50-daily-min-f-0-trade",
    "https://chartink.com/screener/50-22-nw-shesha-magic-buy-love",
    "https://chartink.com/screener/50-bearish-maribozu",
    "https://chartink.com/screener/copy-atr-volume-f-o-200-wkly-rsi-70-new",
    "https://chartink.com/screener/copy-chanakya-bearish-scanner-working-2803"
]
 
       
sheet_id = "1bKrdupQL1LXAOXwmM1YsoN3xoGiMfS7pgzTkQFC3cjw"
worksheet_names = ["p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13","p14","p15","p16","p17","p18","p19","p20","p21","p22","p23","p24","p25","p26","p27","p28","p29"]

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

