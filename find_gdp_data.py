from playwright.sync_api import sync_playwright
import time
import os

def run_gdp_workflow():
    project_folder = os.path.abspath(os.path.dirname(__file__))
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            print("Navigating to Infoshare Stats NZ...")
            page.goto("https://infoshare.stats.govt.nz/", timeout=60000)
            
            # Navigate tree structure automatically
            page.wait_for_selector("text=Economic indicators", timeout=15000)
            print("Expanding 'Economic indicators'...")
            page.click("text=Economic indicators")
            
            gdp_selector = "text=National Accounts - SNA 2008 - SNE"
            page.wait_for_selector(gdp_selector, state="visible", timeout=15000)
            print("Clicking 'National Accounts - SNA 2008 - SNE'...")
            page.click(gdp_selector, force=True)
            
            # Target headline table directly
            target_table = "Series, GDP(P), Chain volume, Seasonally adjusted, Total, Percentage change (Qrtly-Mar/Jun/Sep/Dec)"
            print(f"Waiting for table: '{target_table}'...")
            page.wait_for_selector(f"text={target_table}", timeout=20000)
            print(f"Selecting table: '{target_table}'...")
            page.click(f"text={target_table}", force=True)
            
            # Wait for variable configuration page to load completely
            print("Waiting for variable selection screen...")
            page.wait_for_load_state("networkidle")
            page.wait_for_selector("text=Select variables", timeout=15000)
            time.sleep(1.5)

            # Explicitly click all "Select all" links across the variable boxes
            print("Automatically selecting all variables and full time history...")
            select_all_links = page.locator("text=Select all").all()
            print(f"Found {len(select_all_links)} 'Select all' options. Clicking them...")
            
            for i, link in enumerate(select_all_links):
                try:
                    link.scroll_into_view_if_needed()
                    link.click(force=True)
                    print(f" - Successfully clicked 'Select all' [{i+1}/{len(select_all_links)}]")
                    time.sleep(0.5)
                except Exception as ex:
                    print(f" - Warning: Could not click link {i+1}: {ex}")

            print("\n" + "="*65)
            print(" [READY] Automation complete up to the export screen!")
            print(" 1. Scroll down to the bottom right dropdown in the browser.")
            print(" 2. Change 'Table on screen' to 'Comma delimited (.csv)'.")
            print(" 3. Click 'Go'. Playwright will intercept it automatically!")
            print("="*65 + "\n")

            # Listen for the download event when you click Go manually
            with page.expect_download(timeout=180000) as download_info:
                print("Waiting for you to change format to CSV and click 'Go'...")
            
            download = download_info.value
            
            # Save it explicitly as gdp.csv right in your project folder
            final_file_path = os.path.join(project_folder, "gdp.csv")
            download.save_as(final_file_path)
            
            print(f"\n[SUCCESS] File successfully captured and saved to: {final_file_path}")
            time.sleep(3)

        except Exception as e:
            print(f"\n[ERROR] Step failed: {e}")
        
        finally:
            browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    run_gdp_workflow()