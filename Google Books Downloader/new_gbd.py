import os
import urllib
import traceback
import regex as re
from time import sleep
from seleniumwire import webdriver
from progressbar import progressbar as bar
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


from webdriver_manager.chrome import ChromeDriverManager


def get_book_url(url):
    if re.findall(r"id=[A-Za-z0-9]+", url):
        id_part = re.findall(r"id=[A-Za-z0-9]+", url)[-1]
    else:
        print("Invalid input. Please try again.")
        get_book_url()
        
    return (f"https://books.google.com/books?{id_part}&pg=1&hl=en#v=onepage&q&f=false",
            f"https://books.google.com/books?{id_part}&pg=1&hl=en&f=false&output=embed&source=gbs_embed")

def get_book_data(url):
    """
    Inspects the opened book, returns a
    `str` with its title and author.
    """
    driver.get(url)
    driver.refresh()
    sleep(3)
    title = driver.find_element_by_class_name("gb-volume-title").text
    author = driver.find_element_by_class_name("addmd").text    
    return f"{title} (b{author[1:]})"

def capture_requests(url):
    """
    Scrolls through the whole book,
    returns the requests driver made.
    """
    driver.get(url)
    driver.refresh()
    sleep(5)
    checkpoint = ""
    
    while checkpoint != driver.find_element_by_class_name("pageImageDisplay"):
        checkpoint = driver.find_element_by_class_name("pageImageDisplay")
        checkpoint.click()
        # scrolling ~25 pages
        for i in range(25):
            html = driver.find_element_by_tag_name("body")
            html.click()
            html.send_keys(Keys.SPACE)
        sleep(2)
    return str(driver.requests)

def extract_urls(requests):
    """
    Takes driver's requests as an input,
    returns a `dict` of page image URLs.
    """
    urls = re.findall(r"url='(https:\/\/[^']+content[^']+pg=[A-Z]+([0-9]+)[^']+)(&w=[0-9]+)'", requests)

    return {int(url[1]): url[0] + "&w=69420" for url in urls}



def select_pages(user_input, all_pages):
    """
    Takes the range of pages user specified
    and image URLs of all pages available,
    returns a `dict` with selected pages only.
    """
    ranges = user_input.replace(" ", "").split(",")
    page_numbers = []
    
    if "all" in ranges:
        return all_pages
    while "odd" in ranges:
        page_numbers.extend([i for i in all_pages.items() if i[0] % 2])
        ranges.remove("odd")
    while "even" in ranges:
        page_numbers.extend([i for i in all_pages.items() if i[0] % 2 == 0])
        ranges.remove("even")
    for segment in ranges:
        if "-" in segment:
            a, b = segment.split("-")
            page_numbers.extend([i for i in all_pages.items() if int(a) <= i[0] <= int(b)])
        elif int(segment) in all_pages.keys():
            page_numbers.append((int(segment), all_pages[int(segment)]))

    return dict(set(page_numbers))
    
def get_cookie(url):
    """
    Driver needs to behave like a real
    user to GET page images. This function
    returns a cookie to bribe Google with.
    """
    cookies = []
    driver.get(url)
    driver.refresh()
    
    for request in driver.requests:
        if request.headers:
           for k, v in request.headers.items():
                if k.lower() == "cookie":
                    cookies.append(v)
                    break

    return cookies[0]

def download_imgs(pages, cookie, directory):
    """
    Takes the `dict` of pages to download,
    the cookie to use and the directory
    to save to, and then does the magic.
    """
    proxy = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy)
    opener.addheaders = [("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30"),
                        ("cookie", cookie)]
    urllib.request.install_opener(opener)

    print(pages.items())
    for number, url in pages.items():
        urllib.request.urlretrieve(url, os.path.join(directory, f"page{number}.png"))

def step1(url):
    global book_data, all_pages
    
    from_url = url

    data_url, pages_url = get_book_url(url)
    book_data = get_book_data(data_url)
    print(f"\nWe will now process the pages of \"{book_data}\" one by one. Sit back and relax, as this may take some time, depending on the number of its pages.\n")
    reqs = capture_requests(pages_url)
    all_pages = extract_urls(reqs)
    print("""Now that most of the job is done (yahoo!), it is highly recommended to backup the current progress we have made, so as not to lose it if an error happens to be thrown afterward.
Also, if you would like to download another segment of this book later, the backup will be used then to save your precious time.""")

    

def step2(selection):
    global selected_pages, cookie
    
    try:
        selected_pages = select_pages(selection, all_pages)
        
    except:
        print("Invalid input. Please try again.")
        step2()

    # it's a surprise tool that will help us later
    cookie = get_cookie(list(all_pages.items())[0][1])

def step3():    
    main_directory = ""
    new_directory = os.path.join(main_directory, book_data)
    if not os.path.exists(new_directory):
        os.mkdir(new_directory)

        
    print(f"\nWe will now download all {len(selected_pages)} pages you selected. This will take a minute or two.\n")
    download_imgs(selected_pages, cookie, new_directory)

if __name__ == "__main__":
    global driver
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("prefs", {"safebrowsing.enabled": True})
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    url = "http://books.google.com/books?id=DTtAoKLXuz8C&pg=PA117&dq=a+u&hl=&cd=1&source=gbs_api"
    selection = "1"
    
    try:
        step1(url)
        step2(selection)
        step3()
        
    except Exception as e:
        with open("google-books-downloader crash.log", "w") as log:
            log.write(traceback.format_exc())
        print(f"""
Something went wrong :/

Please make sure that:
-   you are connected to the Internet
-   the book you are trying to download has preview
-   you entered a valid URL of a Google Books book
-   your inputs correspond the formatting
-   you have permission to save/create files in this and the download directories
    
If it still repeats and you think this is an error, please report it on github.com/aprikyan/google-books-downloader.
When reporting, do not forget to attach the following file to the issue:
    {os.path.join(os.getcwd(), "google-books-downloader crash.log")}
""")
        
    else:
        print(f"""
The selected pages were successfully downloaded into the "{book_data}" folder!

Note that for your convenience the pages are saved as images. If you would like to combine them in a PDF (or another format), it might be done using specialized websites and apps.""")
        
        # combining in PDF involves asking about its DPI, size, etc, and
        # it would take much time and RAM, so it's better to leave it to user
