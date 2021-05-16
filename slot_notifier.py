from selenium import webdriver
from slot_notifier_config import SEARCH_BY_SLIDER_XPATH, SEARCH_STATE_XPATH, SEARCH_DISTRICT_XPATH, SEARCH_BUTTON_XPATH, FILTER_BUTTON_18_PLUS_XPATH, SLOTS_TABLE_XPATH
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
from dataclasses import dataclass
import logging
import argparse
import signal
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class VaccineSlot:
    location: str
    slots_count: list


def send_notification(title, body):
    # Taken from: https://wiki.archlinux.org/title/Desktop_notifications#Python
    import gi
    gi.require_version('Gio', '2.0')
    from gi.repository import Gio
    Application = Gio.Application.new("hello.world", Gio.ApplicationFlags.FLAGS_NONE)
    Application.register()
    Notification = Gio.Notification.new(title)
    Notification.set_body(body)
    Icon = Gio.ThemedIcon.new("dialog-information")
    Notification.set_icon(Icon)
    Application.send_notification(None, Notification)


def send_email(receiver_email, slots, state, district):
    import smtplib
    import os
    total_slots_count = sum([slot.slots_count for slot in slots])
    subject = f"{total_slots_count} slots found for {district}, {state}"
    body = "Visit https://selfregistration.cowin.gov.in/ to book a slot\n\nHere is the list of slots available:\n\n"
    for slot in slots:
        body += f"{slot.slots_count} slots available in {slot.location}\n\n"
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(os.environ["GMAIL_ADDRESS"], receiver_email, msg)


class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)
    logger.info("Kill signal receieved.")

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

class VaccineSlotFinder:
    def __init__(self, state, district):
        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280x1696')
        chrome_options.add_argument('--user-data-dir=/tmp/user-data')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.add_argument('--v=99')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--data-path=/tmp/data-path')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--homedir=/tmp')
        chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        self.driver = webdriver.Chrome(options=chrome_options, service_log_path='/tmp/chromedriver.log')
        self.state = state
        self.district = district

    def open_homepage(self):
        self.driver.get("https://www.cowin.gov.in/home")

    def fetch_slots_rows(self):
        slots_table =  self.driver.find_element_by_xpath(SLOTS_TABLE_XPATH)
        slots_rows = slots_table.find_elements_by_xpath("./*")
        if len(slots_rows) == 1 and "No Vaccination center is available for booking." in slots_rows[0].text:
            return []
        return slots_rows

    def fetch_coluums_of_row(self, slots_row):
        return slots_row.find_elements_by_xpath("./div/div/div[2]/ul/li")
    
    def fetch_location_from_row(self, slots_row):
        return slots_row.find_element_by_xpath("./div/div/div[1]").text
    
    def fetch_slots_from_row(self, slots_row):
        location = self.fetch_location_from_row(slots_row)
        columns = self.fetch_coluums_of_row(slots_row)
        slots = []
        for column in columns:
            if column.text != 'NA' and 'Booked' not in column.text:
                slots.append(VaccineSlot(
                    location,
                    int(column.text.split("\n")[0])
                ))
        return slots


    def search_slots(self):
        self.open_homepage()
        time.sleep(2)
        self.driver.find_element_by_xpath(SEARCH_BY_SLIDER_XPATH).click()
        self.driver.find_element_by_xpath(SEARCH_STATE_XPATH).click()
        state_element = self.driver.find_elements_by_xpath(f"//*[contains(text(), '{self.state}')]")[0]
        # ActionChains(self.driver).move_to_element(state_element).perform()
        self.driver.execute_script("return arguments[0].scrollIntoView();", state_element)
        state_element.click()

        self.driver.find_element_by_xpath(SEARCH_DISTRICT_XPATH).click()
        district_element = self.driver.find_elements_by_xpath(f"//*[contains(text(), '{self.district}')]")[0]
        # ActionChains(self.driver).move_to_element(district_element).perform()
        self.driver.execute_script("return arguments[0].scrollIntoView();", district_element)
        district_element.click()
        self.driver.find_element_by_xpath(SEARCH_BUTTON_XPATH).click()
        logger.info(f"Filtered by state:{self.state} and district:{self.district}")
        # self.driver.find_element_by_xpath(FILTER_BUTTON_18_PLUS_XPATH).click()
        # logger.info("Filtered by age 18+")
        time.sleep(1)
        slots_rows = self.fetch_slots_rows()
        logger.info(f"Found {len(slots_rows)} vaccine centres in list.")
        all_slots = []
        for slots_row in slots_rows:
            row_slots = self.fetch_slots_from_row(slots_row)
            all_slots.extend(row_slots)
        return all_slots

def vaccine_slot_notifier(state, district, email_address):
    logger.info("Starting vaccine slot finder")
    slot_finder = VaccineSlotFinder(args.state, args.district)
    logger.info("Starting vaccince slot search.")
    try:
        slots_available = slot_finder.search_slots()
    except Exception:
        slots_available = []
        logger.exception("Exception raised while searching for slots")

    if not slots_available:
        logger.info("No slots available. :(")
    else:
        slots_message = "\n".join([str(slot) for slot in slots_available])
        total_slots_count = sum([slot.slots_count for slot in slots_available])
        logger.info(f"{total_slots_count} slots found. The following list of slots are available.\n{slots_message}")
        if args.email_address:
            send_email(args.email_address, slots_available, args.state, args.district)


def vaccine_slot_periodic_notifier(state, district, email_address, search_interval_seconds, renotification_interval_seconds):
    logger.info("Starting vaccine slot finder")
    slot_finder = VaccineSlotFinder(args.state, args.district)
    killer = GracefulKiller()
    while not killer.kill_now:
        logger.info("Starting vaccince slot search.")
        try:
            slots_available = slot_finder.search_slots()
        except Exception:
            slots_available = []
            logger.exception("Exception raised while searching for slots")

        if not slots_available:
            logger.info("No slots available. :(")
            logger.info(f"Sleeping for {args.search_interval_seconds} seconds.")
            time.sleep(args.search_interval_seconds)
        else:
            slots_message = "\n".join([str(slot) for slot in slots_available])
            total_slots_count = sum([slot.slots_count for slot in slots_available])
            logger.info(f"{total_slots_count} slots found. The following list of slots are available.\n{slots_message}")
            # send_notification("Covid vaccine slot finder", f"Found total {total_slots_count} slots in {args.district}, {args.state}")
            if args.email_address:
                send_email(args.email_address, slots_available, args.state, args.district)
            time.sleep(args.renotification_interval_seconds)
            logger.info(f"Sleeping for {args.renotification_interval_seconds} seconds.")

        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("state")
    parser.add_argument("district")
    parser.add_argument("--search-interval-seconds", type=int, default=30)
    parser.add_argument("--renotification-interval-seconds", type=int, default=60)
    parser.add_argument('--email-address', nargs='+', default=[])
    args = parser.parse_args()
    # vaccine_slot_periodic_notifier(args.state, args.district, args.email_address, args.search_interval_seconds, args.renotification_interval_seconds)
    vaccine_slot_notifier(args.state, args.district, args.email_address)
