from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


url = "https://robotsparebinindustries.com/#/robot-order"
url_csv= "https://robotsparebinindustries.com/orders.csv"
@task
def order_robots_from_robotsparebin():
    browser.configure(
        slowmo=100,
    )
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    download_csv_file()
    open_robot_order_website()
    close_annoying_modal()
    read_csv_as_table()
    create_zip()


def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto(url)

def close_annoying_modal():
    """Accept the terms"""
    page = browser.page()
    page.wait_for_selector('.btn.btn-dark')
    page.click("button:text('OK')")

def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url_csv, overwrite=True)

def read_csv_as_table():
    """Read data from CSV and fill in the order form"""
    tables = Tables()
    table = tables.read_table_from_csv("orders.csv")
    for row in table:
        fill_and_submit_order_form(row)

def fill_and_submit_order_form(order_bot):
    """Fills in the orders data and click the 'Order' button"""
    page = browser.page()
    try:
        # Fill out data
        page.select_option("#head", str(order_bot["Head"]))
        number=order_bot["Body"]
        page.click(f"#id-body-{number}")
        page.fill('[placeholder="Enter the part number for the legs"]', order_bot["Legs"])
        page.fill("#address", order_bot["Address"])
        page.click("button:text('order')")
        # Wait for the page to load
        page.wait_for_selector("#order-another", timeout=5000)  # Wait up to 5 seconds)
        store_receipt_as_pdf(order_bot)
        screenshot_robot(order_bot)
        embed_screenshot_to_receipt(order_bot)
        page.click("#order-another")
        #click_ok
        page.wait_for_selector('.btn.btn-dark')
        page.click("button:text('OK')")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Reloading the page and restarting the process...")
        browser.goto(url)
        fill_and_submit_order_form(order_bot)


def store_receipt_as_pdf(order_seq):
    """Export the order to a pdf file"""
    order=order_seq["Order number"]
    page = browser.page()
    order_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(order_html, f"output/receipts/receipt_{order}.pdf")

def screenshot_robot(order_seq):
    """Take a screenshot of the page"""
    order=order_seq["Order number"]
    page = browser.page()
    element = page.query_selector("#robot-preview-image")
    element.screenshot(path=f"output/receipts/receipt_{order}.png")

def embed_screenshot_to_receipt(order_seq):
    pdf = PDF()
    order=order_seq["Order number"]
    screenshot=f"output/receipts/receipt_{order}.png"
    pdf_file=f"output/receipts/receipt_{order}.pdf"
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)


def create_zip():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts/', 'output/receipts.zip', recursive=True)