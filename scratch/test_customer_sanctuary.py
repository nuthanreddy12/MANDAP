from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', headless=True)
page = browser.new_page()
page.goto('http://127.0.0.1:5173/customer/login')
page.fill('input[type="email"]', 'priya.mehra@gmail.com')
page.fill('input[type="password"]', 'Password123!')
page.click('button[type="submit"]')
page.wait_for_url('**/customer/dashboard')
page.wait_for_selector('text=Priya Mehra', timeout=8000)
print('SUCCESS: Found text Priya Mehra rendered in live customer dashboard!')
browser.close()
p.stop()

