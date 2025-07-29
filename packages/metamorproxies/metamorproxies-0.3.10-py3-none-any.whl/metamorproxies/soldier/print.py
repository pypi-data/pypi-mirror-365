from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
class PrintWeb:
    """
    A class to take a screenshot of a given website.
    """
    
    def __init__(self, url, output_path="screenshot.png"):
        """
        Initializes the PrintWeb instance.

        Args:
            url (str): The URL of the website to capture.
            output_path (str, optional): The path where the screenshot will be saved. Defaults to "screenshot.png".
        """
        self.url = url
        self.output_path = output_path
        
    def set_path(self, output_path):
        """
        Updates the output path for saving the screenshot.

        Args:
            output_path (str): The new file path where the screenshot should be saved.
        """
        self.output_path = output_path
    
    
    def setup_driver(self):
        """
        Configura e retorna uma instância do Chrome WebDriver em modo headless.
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,800")

        # Cria um diretório temporário exclusivo para o user-data-dir
        temp_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_dir}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver


    def take_screenshot(self):
        """
        Captures a screenshot of the specified website and saves it as a PNG file.
        """
        driver = self.setup_driver()
        driver.get(self.url)
        driver.save_screenshot(self.output_path)
        driver.quit()
        print(f"Screenshot site saved as {self.output_path}")

# Example usage
