from playwright.sync_api import sync_playwright

def create_indicator(x, y):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto('https://vaughan.perfectmind.com/25076/Menu/SocialSite/MemberCheckout?shoppingCartKey=4b716026-089f-4eb8-b389-ed9175db74b8&userName=hojustin.1128%40gmail.com')
        
        # Create red dot
        page.evaluate("""([x, y]) => {
            const indicator = document.createElement('div');
            indicator.style.position = 'absolute';
            indicator.style.left = x + 'px';
            indicator.style.top = y + 'px';
            indicator.style.width = '10px';
            indicator.style.height = '10px';
            indicator.style.backgroundColor = 'red';
            indicator.style.borderRadius = '50%';
            indicator.style.transform = 'translate(-50%, -50%)';
            indicator.style.zIndex = '9999';
            indicator.style.boxShadow = '0 0 5px rgba(0,0,0,0.5)';
            indicator.id = 'playwright-coord-indicator';
            document.body.appendChild(indicator);
        }""", [x, y])
        
        # Optional crosshair lines
        page.evaluate("""([x, y]) => {
            // Horizontal line
            const hLine = document.createElement('div');
            hLine.style.position = 'absolute';
            hLine.style.left = '0';
            hLine.style.top = y + 'px';
            hLine.style.width = '100%';
            hLine.style.height = '1px';
            hLine.style.backgroundColor = 'rgba(255,0,0,0.5)';
            hLine.style.zIndex = '9998';
            document.body.appendChild(hLine);
            
            // Vertical line
            const vLine = document.createElement('div');
            vLine.style.position = 'absolute';
            vLine.style.left = x + 'px';
            vLine.style.top = '0';
            vLine.style.width = '1px';
            vLine.style.height = '100%';
            vLine.style.backgroundColor = 'rgba(255,0,0,0.5)';
            vLine.style.zIndex = '9998';
            document.body.appendChild(vLine);
        }""", [x, y])
        
        input("Press Enter to close the browser...")
        browser.close()

# Example usage
create_indicator(300, 430)