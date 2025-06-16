
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import stat
import glob
import subprocess
import shutil

class DriverManager:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def check_system_dependencies(self):
        """Check if Chrome and ChromeDriver are available in the system."""
        print("\n🔍 SYSTEM DEPENDENCY CHECK:")
        
        # Check if we're in Railway environment
        is_railway = os.environ.get("RAILWAY_ENVIRONMENT")
        print(f"   Railway Environment: {is_railway}")
        
        # Check Chrome binary locations
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable", 
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/chrome",
            "/usr/bin/chromium",
            "/snap/bin/chromium"
        ]
        
        chrome_found = None
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"   ✅ Chrome found at: {path}")
                chrome_found = path
                break
            else:
                print(f"   ❌ Chrome not found at: {path}")
        
        # Check ChromeDriver locations
        driver_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/opt/homebrew/bin/chromedriver",
            "/snap/bin/chromedriver"
        ]
        
        driver_found = None
        for path in driver_paths:
            if os.path.exists(path):
                print(f"   ✅ ChromeDriver found at: {path}")
                # Check if it's executable
                if os.access(path, os.X_OK):
                    print(f"   ✅ ChromeDriver is executable")
                    driver_found = path
                else:
                    print(f"   ⚠️  ChromeDriver exists but not executable")
                    try:
                        os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                        print(f"   ✅ Made ChromeDriver executable")
                        driver_found = path
                    except Exception as e:
                        print(f"   ❌ Could not make executable: {e}")
                break
            else:
                print(f"   ❌ ChromeDriver not found at: {path}")
        
        # Try to get Chrome version
        if chrome_found:
            try:
                result = subprocess.run([chrome_found, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   ✅ Chrome version: {result.stdout.strip()}")
                else:
                    print(f"   ❌ Chrome version check failed: {result.stderr}")
            except Exception as e:
                print(f"   ❌ Chrome version check error: {str(e)}")
        
        # Try to get ChromeDriver version
        if driver_found:
            try:
                result = subprocess.run([driver_found, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   ✅ ChromeDriver version: {result.stdout.strip()}")
                else:
                    print(f"   ❌ ChromeDriver version check failed: {result.stderr}")
            except Exception as e:
                print(f"   ❌ ChromeDriver version check error: {str(e)}")
        
        return chrome_found, driver_found
    
    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options."""
        print("\n🚀 SETTING UP CHROME WEBDRIVER")
        
        try:
            # Check system dependencies first
            chrome_binary, driver_path = self.check_system_dependencies()
            
            chrome_options = Options()
            
            # Enhanced Railway/Production optimizations
            if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RENDER") or os.environ.get("HEROKU"):
                print("🚂 Production environment detected")
                
                # Essential headless options for production
                chrome_options.add_argument("--headless=new")  # Use new headless mode
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-software-rasterizer")
                chrome_options.add_argument("--disable-background-timer-throttling")
                chrome_options.add_argument("--disable-backgrounding-occluded-windows")
                chrome_options.add_argument("--disable-renderer-backgrounding")
                chrome_options.add_argument("--disable-features=TranslateUI")
                chrome_options.add_argument("--disable-ipc-flooding-protection")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--single-process")
                chrome_options.add_argument("--no-zygote")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins")
                chrome_options.add_argument("--disable-images")
                chrome_options.add_argument("--disable-javascript")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # Memory optimization
                chrome_options.add_argument("--memory-pressure-off")
                chrome_options.add_argument("--max_old_space_size=4096")
                
                if not chrome_binary:
                    # Try alternative Chrome detection methods
                    alternative_paths = [
                        "/usr/bin/google-chrome-stable",
                        "/usr/bin/chromium-browser", 
                        "/usr/bin/chromium",
                        "/snap/bin/chromium"
                    ]
                    
                    for alt_path in alternative_paths:
                        if os.path.exists(alt_path):
                            chrome_binary = alt_path
                            print(f"   🔄 Using alternative Chrome: {chrome_binary}")
                            break
                
                if not chrome_binary:
                    raise Exception("❌ Chrome binary not found. Install with: apt-get update && apt-get install -y google-chrome-stable")
                
                if not driver_path:
                    raise Exception("❌ ChromeDriver not found. Install with: apt-get install -y chromium-chromedriver")
                
                chrome_options.binary_location = chrome_binary
                service = Service(driver_path)
                print(f"   Using Chrome: {chrome_binary}")
                print(f"   Using ChromeDriver: {driver_path}")
                
            else:
                # Local development settings
                print("💻 Local development environment detected")
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--window-size=1920,1080")
                
                if driver_path:
                    service = Service(driver_path)
                    print(f"   Using system ChromeDriver: {driver_path}")
                else:
                    # Try webdriver-manager as fallback
                    print("   Attempting to download ChromeDriver...")
                    try:
                        downloaded_path = ChromeDriverManager().install()
                        print(f"   Downloaded ChromeDriver to: {downloaded_path}")
                        
                        # Handle THIRD_PARTY_NOTICES issue
                        if 'THIRD_PARTY_NOTICES' in downloaded_path:
                            dir_path = os.path.dirname(downloaded_path)
                            possible_drivers = glob.glob(os.path.join(dir_path, "*chromedriver*"))
                            for possible in possible_drivers:
                                if 'THIRD_PARTY_NOTICES' not in possible and os.access(possible, os.X_OK):
                                    driver_path = possible
                                    print(f"   Found actual ChromeDriver: {driver_path}")
                                    break
                        else:
                            driver_path = downloaded_path
                        
                        if not driver_path:
                            raise Exception("Could not locate ChromeDriver after download")
                        
                        # Ensure executable permissions
                        os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                        service = Service(driver_path)
                        
                    except Exception as e:
                        print(f"   WebDriver manager failed: {str(e)}")
                        raise Exception(f"ChromeDriver setup failed: {str(e)}")
            
            print("🔧 Initializing WebDriver...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            print("✅ Chrome WebDriver initialized successfully")
            
            # Test the driver
            print("🧪 Testing WebDriver functionality...")
            self.driver.get("about:blank")
            print("✅ WebDriver test successful")
            
        except Exception as e:
            error_msg = f"💥 WebDriver setup failed: {str(e)}"
            print(error_msg)
            print(f"   Exception type: {type(e).__name__}")
            
            # Enhanced error diagnostics
            if "Chrome binary" in str(e) or "chrome" in str(e).lower():
                print("\n🔍 CHROME INSTALLATION ISSUE:")
                print("   Try: apt-get update && apt-get install -y google-chrome-stable")
                print("   Or: apt-get install -y chromium-browser")
            elif "chromedriver" in str(e).lower():
                print("\n🔍 CHROMEDRIVER ISSUE:")
                print("   Try: apt-get install -y chromium-chromedriver")
                print("   Check version compatibility between Chrome and ChromeDriver")
            elif "timeout" in str(e).lower():
                print("\n🔍 TIMEOUT ISSUE:")
                print("   Chrome may be taking too long to start")
                print("   Consider increasing timeout or checking system resources")
            
            raise Exception(f"WebDriver initialization failed: {str(e)}")
    
    def get_driver(self):
        """Get the WebDriver instance."""
        if not self.driver:
            raise Exception("WebDriver not initialized. Call setup_driver() first.")
        return self.driver
    
    def close(self):
        """Close the WebDriver safely."""
        try:
            if hasattr(self, 'driver') and self.driver:
                print("🔒 Closing WebDriver...")
                self.driver.quit()
                self.driver = None
                print("✅ WebDriver closed successfully")
        except Exception as e:
            print(f"⚠️  Error closing WebDriver: {str(e)}")
            # Force cleanup
            try:
                if hasattr(self, 'driver') and self.driver:
                    self.driver = None
            except:
                pass
