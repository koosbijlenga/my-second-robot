from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables 
from RPA.PDF import PDF
from RPA.Archive import Archive
import time
import os


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    if not os.path.exists("output/receipts"):
        os.makedirs("output/receipts") 
    open_the_intranet_website()
    download_csv_file()
    orders = get_orders()
    for single_order in orders:
        close_annoying_modal()
        fill_the_form(single_order)
        filename_pdf=store_receipt_as_pdf(single_order["Order number"])
        filename_scr=screenshot_robot(single_order["Order number"])
        embed_screenshot_to_receipt(filename_scr, filename_pdf)
        another_order()
    archive_receipts()
    

def open_the_intranet_website():
    """Open the actual website to order"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_csv_file():
    """Download the csv file with orders"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    """read data from csv file into a table"""
    table = Tables()
    return (table.read_table_from_csv("orders.csv",header=True))
    
def close_annoying_modal():
    """Close the pop-up message after opening the website"""
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(order):
    """Put the values in the website for ordering"""
    submit_error = True
    page = browser.page()
    page.select_option("#head", order["Head"])
    page.click("#id-body-"+ order["Body"])
    page.fill("xpath=//div[@class='mb-3'][3]/label[1]", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("button:text('Preview')")
    while submit_error:
        page.click("button:text('ORDER')")
        time.sleep (1)
        if page.query_selector("xpath=//div[@class='alert alert-danger']") == None:
            submit_error = False
        

def another_order():
    """click on the other order button"""
    page=browser.page()
    page.click("#order-another")
    
def store_receipt_as_pdf(order_number):
    """copies the receipt into a PDF file"""
    page=browser.page()
    order_html=page.locator("#receipt").inner_html()
    pdf_file=PDF()
    filename="output/receipts/receipt-"+order_number+".pdf"
    pdf_file.html_to_pdf(order_html,filename)
    return (filename)

def screenshot_robot(order_number):
    """takes a screenshot of the robot page"""
    page=browser.page()
    filename="output/receipts/receipt-"+order_number+".png"
    page.screenshot(path=filename)
    return (filename)

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """append the screenshot to the existing pdf-file"""
    pdf=PDF()
    pdf.add_files_to_pdf([screenshot],pdf_file,append=True)

def archive_receipts():
    """create a zip file of the generated pdf files"""
    archive=Archive()
    archive.archive_folder_with_zip(folder="output/receipts",archive_name="output/receipts.zip",recursive=False,include="*.pdf")
