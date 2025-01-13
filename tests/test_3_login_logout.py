import unittest
import json
from time import sleep
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException


# 서버 url = AWS devicefarm server url
# local server url = 'http://localhost:4723'
# AWS devicefarm server url = "http://127.0.0.1:4723/wd/hub"
appiumServerUrl = "http://127.0.0.1:4723/wd/hub"
# 계정 정보 세팅
json_filepath = './account.json'
with open(json_filepath, 'r') as file:
    data = json.load(file)

test_id = data["test_id"]
test_pw = data["test_pw"]

capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='Android',
    appPackage='com.etoos.app.wm',
    appActivity='com.etoos.app.wm.ui.at.SplashActivity',
    ignoreHiddenApiPolicyError=True, # appium 허용하지 않는 App을 사용 가능하도록 변경
    autoGrantPermissions=True, # Android 시스템 동의 - 강제 허용 설정 >> 카메라, 마이크 사용 등등 모두 허용 처리
    noReset = False
    # autoWebview=True # Webview context 전환 허용
)


class loginLogout(unittest.TestCase):

    # setUp > 1개의 테스트마다 자동으로 호출하는 사전 코드 / 실행 중 예외 사항 발생 시 테스트 메서드는 실행하지 않음
    def setUp(self):
        self.driver = webdriver.Remote(
            command_executor=appiumServerUrl, options=UiAutomator2Options().load_capabilities(capabilities))

    # 테스트 실행
    def test_01_init(self):
        # APP 실행 대기
        wait = WebDriverWait(self.driver, 30)  # Timeout 대기 시간
        self.driver.activate_app(app_id='com.etoos.app.wm')  # 워드마스터 앱 실행 후 app 강제 종료되는 이슈 방지
        sleep(5)
        # 앱 초기화 막기 위해 capabilities 변경
        capabilities["noReset"] = True

        # Splash 팝업 확인 버튼 클릭
        try:
            el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/btnConfirm')))
            el.click()
        except TimeoutException:
            print("Confirm button not found. Continuing.")

        # 메인 화면 진입
        sleep(5)

    def test_02_login(self):
        wait = WebDriverWait(self.driver, 10)
        # 메인 진입 시간 대기
        sleep(5)

        # 마이룸 클릭
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
        el.click()
        sleep(10)

        ### 통합회원 로그인
        # webview element 활성화

        try:
            el = wait.until(EC.visibility_of_element_located((AppiumBy.CLASS_NAME, "android.webkit.WebView")))
            el.click()
        except TimeoutException:
            print("WebView not found. Continuing.")
            return
        sleep(3)

        # id/pw 입력
        input_area = wait.until(EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
        input_area[0].send_keys(test_id)  # id 입력
        sleep(3)
        input_area[1].send_keys(test_pw)  # pw 입력
        sleep(3)

        # 로그인 버튼 클릭
        el = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@text="로그인"]')
        el.click()  # 로그인 버튼 클릭
        sleep(5)

        '''
        예외 사항. 1 - 비밀번호 변경 화면 > 다음에 변경하기 check
        '''
        try:
            el = wait.until(EC.visibility_of_element_located((AppiumBy.XPATH, '//android.webkit.WebView[@text="통합회원"]/android.view.View[1]/android.view.View[2]/android.view.View[5]/android.view.View[1]')))
            el.click()  # 다음에 변경하기 버튼 클릭
            print("예외사항 1: 다음에 변경하기 클릭 completed")
            sleep(5) # 메인 진입 대기
        except TimeoutException:
            pass

        '''
        예외 사항. 2 - 중복 로그인 팝업 > check
        '''
        try:
            el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/btnConfirm')))
            el.click()  # 확인 버튼 클릭
            print("예외사항 2: 중복 로그인 확인 버튼 click completed")
            sleep(5) # 메인 진입 대기
        except TimeoutException:
            pass

    def test_03_loginHold(self):
        # 앱 종료
        self.terminate_app_with_retry('com.etoos.app.wm', 10) # 앱 종료
        sleep(5)  # 앱 종료 대기 시간

        # 앱 재실행
        self.driver.activate_app(app_id='com.etoos.app.wm')
        self.wait_for_app_foreground('com.etoos.app.wm', 10)
        sleep(5)

        sleep(5)  # 앱 재실행 대기 시간

        # 백그라운드 이동
        self.driver.background_app(5)

        # 앱 재실행
        self.driver.activate_app(app_id='com.etoos.app.wm')
        self.wait_for_app_foreground('com.etoos.app.wm', 10)
        sleep(5)

        sleep(5)  # 앱 재실행 대기 시간

    def test_04_logout(self):
        wait = WebDriverWait(self.driver, 30)
        # 메인 진입 후 마이룸 클릭
        try:
            el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
            el.click()
            sleep(5)
        except TimeoutException:
            print("My Room button not found. Test failed.")
            return

        # 로그아웃 버튼 클릭
        try:
            el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/btnLogout')))
            el.click()
            sleep(3)
        except TimeoutException:
            print("Logout button not found. Test failed.")
            return

        # 확인 버튼 클릭
        try:
            el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/btnConfirm')))
            el.click()
            sleep(3)
        except TimeoutException:
            print("Confirm button not found. Continuing.")

    def terminate_app_with_retry(self, app_id, retries=5):
        for _ in range(retries):
            try:
                self.driver.terminate_app(app_id=app_id)
                return
            except WebDriverException as e:
                print(f"Error terminating app: {e}. Retrying...")
                sleep(1)
        print(f"Failed to terminate app {app_id} after {retries} retries.")

    def wait_for_app_foreground(self, app_id, retries=5):
        for _ in range(retries):
            app_state = self.driver.query_app_state(app_id=app_id)
            if app_state == 4:  # 4 = foreground
                print("App is in foreground.")
                return
            sleep(1)
        print(f"App {app_id} not in foreground after {retries} retries.")

    # tearDown > 테스트 메서드 실행 후 호출되는 코드 / setUp이 성공한다면 테스트 성공 여부에 상관없이 실행
    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == '__main__':
    unittest.main() # 테스트 스크립트에 명령행 인터페이스 제공
