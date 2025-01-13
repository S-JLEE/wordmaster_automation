import unittest
import json
import os
from time import sleep
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


# 서버 url = AWS devicefarm server url
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


class mainBannerClick(unittest.TestCase):

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
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnConfirm')
        wait.until(EC.visibility_of(el))
        el.click()

        # 메인 화면 진입
        sleep(5)

    def test_02_bannerClick(self):
        # 메인 진입 시간 대기
        sleep(5)

        title = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/bannerTitle').text
        if title == "실력진단 테스트":
            el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/bntBannerMove')
            el.click()
            sleep(5)
            # 종료 버튼 클릭 > 메인 이동
            el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnClose')
            el.click()
            sleep(5)
        else:
            # 외부 페이지 이동
            el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/bntBannerMove')
            el.click()
            sleep(10)
            # 앱으로 복귀
            current_app_package = self.driver.current_package
            self.driver.terminate_app(app_id=current_app_package)  # 이동한 앱 종료
            sleep(5)
            self.driver.activate_app(app_id='com.etoos.app.wm')  # 워드마스터 앱 재실행
            sleep(5)


    # tearDown > 테스트 메서드 실행 후 호출되는 코드 / setUp이 성공한다면 테스트 성공 여부에 상관없이 실행
    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == '__main__':
    unittest.main() # 테스트 스크립트에 명령행 인터페이스 제공
