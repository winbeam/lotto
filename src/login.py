#!/usr/bin/env python3
import os
import time
from os import environ
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright
import sys
import traceback
from script_reporter import ScriptReporter

# Robustly match .env file
def load_environment():
    """
    .env 파일을 찾아 로드합니다.
    우선순위:
    1. src/ 상위 디렉토리 (프로젝트 루트)
    2. 현재 작업 디렉토리
    """
    # 1. Check project root (relative to this file)
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / '.env'
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        return

    # 2. Check current working directory
    cwd_env = Path.cwd() / '.env'
    if cwd_env.exists():
        load_dotenv(dotenv_path=cwd_env)
        return
        
    # 3. Last fallback: try default load_dotenv (searches up tree)
    load_dotenv()

load_environment()

USER_ID = environ.get('USER_ID')
PASSWD = environ.get('PASSWD')

SESSION_PATH = "/tmp/dhlotto_session.json"

def save_session(context, path=SESSION_PATH):
    """
    Saves the current browser context state (cookies, local storage) to a file.
    """
    context.storage_state(path=path)
    print(f"Session saved to {path}")


def login(page: Page) -> None:
    """
    동행복권 사이트에 로그인합니다.
    이미 로그인되어 있는 경우를 체크하고, 알림창(alert)을 자동으로 처리합니다.
    """
    if not USER_ID or not PASSWD:
        raise ValueError("USER_ID or PASSWD not found in environment variables.")
    
    # 0. Setup alert handler to automatically accept any alerts (like session timeout alerts)
    page.on("dialog", lambda dialog: dialog.accept())

    print('Starting login process...')
    
    # 1. Check if already logged in by looking for "로그아웃" link
    # We do a quick check on the main page first
    try:
        print("Checking session on main page...")
        page.goto("https://www.dhlottery.co.kr/main.do", timeout=15000)
        if page.get_by_text("로그아웃").first.is_visible(timeout=5000):
            print("Already logged in (detected logout button)")
            return
    except Exception:
        pass # Continue to explicit login if check fails

    # 2. Go to login page
    print("Navigating to login page...")
    page.goto("https://www.dhlottery.co.kr/login", timeout=30000, wait_until="domcontentloaded")
    
    # 3. Check if we were redirected away from login (means already logged in)
    if "/login" not in page.url and "method=login" not in page.url:
        if page.get_by_text("로그아웃").first.is_visible(timeout=5000):
            print("Already logged in (redirected from login page)")
            return

    # 4. Fill login form
    try:
        # The selector might be #inpUserId
        print("Checking login form...")
        # If we are not on login page, we might be already logged in
        if "/login" not in page.url and "method=login" not in page.url:
             if page.locator(".btn_logout").is_visible(timeout=2000) or page.get_by_text("로그아웃").first.is_visible(timeout=2000):
                 print("Already logged in (detected via URL and logout button)")
                 return

        page.wait_for_selector("#inpUserId", timeout=10000)
        
        # Check if already filled (autofill)
        existing_id = page.locator("#inpUserId").input_value()
        if existing_id == USER_ID:
            print(f"ID '{USER_ID}' is already filled.")
        else:
            page.locator("#inpUserId").fill(USER_ID)
            
        existing_pw = page.locator("#inpUserPswdEncn").input_value()
        if existing_pw:
            print("Password is already filled.")
        else:
            page.locator("#inpUserPswdEncn").fill(PASSWD)
        
        # Click login button
        print("Clicking login button...")
        page.click("#btnLogin")
    except Exception as e:
        # If we can't find the input, maybe we ARE logged in but visibility check failed
        if page.get_by_text("로그아웃").first.is_visible(timeout=5000) or "mypage" in page.url:
            print("Already logged in (detected after wait failure)")
            return
        raise Exception(f"Login failed or inputs not found: {e}")

    # 5. Wait for navigation and verify login
    try:
        print("Waiting for login completion...")
        page.get_by_text("로그아웃").first.wait_for(timeout=15000)
        print('Logged in successfully')
    except Exception:
        print("Login verification timed out. Checking content...")
        content = page.content()
        if "로그아웃" in content:
            print('Logged in successfully (detected logout button in content)')
        elif "아이디 또는 비밀번호가 일치하지 않습니다" in content:
            raise Exception("Login failed: Invalid ID or password.")
        else:
            if "/login" in page.url:
                 raise Exception(f"Login failed: Still on login page ({page.url})")
            print(f"Assuming login might have worked (URL: {page.url})")

    # Give a bit more time for session cookies to be stable across subdomains
    time.sleep(3)


def main():
    """
    Standalone login script that saves the session for other scripts to use.
    """
    from playwright.sync_api import sync_playwright
    sr = ScriptReporter("Login Session")
    
    with sync_playwright() as playwright:
        try:
            print("Launching browser for initial login...")
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            sr.stage("LOGIN")
            login(page)
            
            sr.stage("SAVE_SESSION")
            save_session(context)
            
            print("Login successful and session persisted.")
            sr.success({"session_path": SESSION_PATH})
            
            context.close()
            browser.close()
        except Exception:
            sr.fail(traceback.format_exc())
            sys.exit(1)

if __name__ == "__main__":
    main()

