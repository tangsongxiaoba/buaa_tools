from playwright.sync_api import Playwright, sync_playwright
import json, os, shutil
import urllib.request as urlreq
from PIL import Image

course_id = "46438"
sub_id = "1750818"
stu_id = "23371xxx"
stu_pwd = "xxxxxxxx"

if not os.path.exists(course_id):
    os.makedirs(course_id)

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://sso.buaa.edu.cn/login?service=https%3A%2F%2Fyjapi.msa.buaa.edu.cn%2Fcasapi%2Findex.php%3Fforward%3Dhttps%253A%252F%252Fclassroom.msa.buaa.edu.cn%252F%26r%3Dauth%252Flogin%26tenant_code%3D21")
    page.locator("#loginIframe").content_frame.get_by_role("textbox", name="请输入学工号").click()
    page.locator("#loginIframe").content_frame.get_by_role("textbox", name="请输入学工号").fill(stu_id)
    page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").click()
    page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").fill(stu_pwd)
    page.locator("#loginIframe").content_frame.get_by_role("button", name="登录").click()
    url = f"https://yjapi.msa.buaa.edu.cn/courseapi/v3/multi-search/get-course-detail?course_id={course_id}&student={stu_id}"
    page.goto(url)
    # page.wait_for_timeout(1000)
    raw_text = json.loads(page.locator("body").text_content())
    raw_text = raw_text["data"]["sub_list"]
    sublist = {}
    for year in raw_text:
        for month in raw_text[year]:
            for day in raw_text[year][month]:
                co = raw_text[year][month][day]
                date = f"{year:>04}{month:>02}{day:>02}"
                if co[0]["show"] == "yes":
                    sublist[date] = co[0]["id"]
    for sub in sublist:
        sub_id = sublist[sub]
        url = f"https://classroom.msa.buaa.edu.cn/pptnote/v1/schedule/search-ppt?course_id={course_id}&sub_id={sub_id}"
        page.goto(url)
        # page.wait_for_timeout(1000)
        text = json.loads(page.locator("body > pre").text_content())
        folder_path = cache + "/" + sub
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        imgs = []
        for x in text["list"]:
            co = json.loads(x["content"])
            name = co["created"]
            url = co["pptimgurl"]
            img_path = f"{folder_path}/{name}.jpg"
            urlreq.urlretrieve(url, img_path)
            imgs.append(img_path)
        pdf = f"{course_id}/{sub}.pdf"
        images = [Image.open(img) for img in imgs]
        if len(images) == 0:
            continue
        elif len(images) == 1:
            images[0].save(pdf)
        else:
            images[0].save(pdf, save_all=True, append_images=images[1:])
        # page.pause()
    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    cache = f"{course_id}/.cache"
    if not os.path.exists(cache):
        os.makedirs(cache)
    run(playwright)
    shutil.rmtree(cache)
