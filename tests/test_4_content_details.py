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
from selenium.common.exceptions import NoSuchElementException, TimeoutException


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


class contentActions(unittest.TestCase):

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

    def test_02_login(self):
        wait = WebDriverWait(self.driver, 10)
        # 메인 진입 시간 대기
        sleep(5)

        # 마이룸 클릭
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
        el.click()
        sleep(10) # 통합회원 로그인 화면 출력 시간 대기

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
        input_area = self.driver.find_elements(by=AppiumBy.CLASS_NAME, value='android.widget.EditText')
        input_area[0].send_keys(test_id)  # id 입력
        sleep(3)
        input_area[1].send_keys(test_pw)  # pw 입력
        sleep(3)

        # 로그인 버튼 클릭
        el = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@text="로그인"]')
        el.click()  # 로그인 버튼 클릭
        sleep(5)

    def test_03_downloadContent(self):
        """
        1. 학습관을 이동한 뒤 다운로드를 진행 > 하단의 코드는 이것으로 작성됨
        2. or 메인 화면에서 다운로드를 시도 > 이전에 화면 로딩 시간으로 element가 검색되지 않는 이슈가 있었음
        """

        # 학습관 클릭
        wait = WebDriverWait(self.driver, 30)
        el = self.driver.find_element(by=AppiumBy.ID, value="com.etoos.app.wm:id/nav_study_room")
        wait.until(EC.visibility_of(el))
        el.click()
        sleep(4)

        # 컨텐츠 다운로드
        buttons = self.driver.find_elements(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnContentsAction')
        buttons[0].click()
        sleep(10)

        # 다운로드 진행 중일 경우 1초마다 다운로드 상태인지 확인
        try:
            while True:
                if self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/progress') is False:
                    break
                else:
                    sleep(2)
        except NoSuchElementException:
            pass
    def test_04_contentsMain(self):
        # 학습하기 버튼 클릭
        wait = WebDriverWait(self.driver, 30)
        buttons = self.driver.find_elements(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnContentsAction')
        wait.until(EC.visibility_of(buttons[0]))
        buttons[0].click()
        sleep(5)
    def test_05_dayOneFullProgress(self):
        # DAY1 단어책 진입
        wait = WebDriverWait(self.driver, 30)
        days = self.driver.find_elements(by=AppiumBy.ID, value="com.etoos.app.wm:id/txtDay")
        wait.until(EC.visibility_of(days[0]))
        days[0].click()
        sleep(5)

        # I know 절반 클릭
        index_num = int(self.driver.find_element(by=AppiumBy.ID, value="com.etoos.app.wm:id/txtIndicator").text.split("/")[1])
        for num in range(index_num // 2):
            el = self.driver.find_element(by=AppiumBy.ID, value="com.etoos.app.wm:id/mTextViewKnow")
            el.click()
            sleep(2)

        # I Don't know 절반 클릭
        for num in range(index_num // 2):
            el = self.driver.find_element(by=AppiumBy.ID, value="com.etoos.app.wm:id/mTextViewDoNotKnow")
            el.click()
            sleep(2)

        # 확인 버튼 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value="com.etoos.app.wm:id/btnConfirm")
        el.click()
        sleep(4) # 콘텐츠 메인 이동 시간 확보

    def test_06_dayOneTest(self):
        # DAY 1 테스트 버튼 클릭
        contents = self.driver.find_elements(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnTest')
        contents[0].click()
        sleep(3)

        # 문제 개수 영역 선택 및 입력
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/questAmt')
        # el.click()
        el.send_keys("5")
        sleep(3)

        # 아래로 스크롤링 - element 노출을 위함
        screen_size = self.driver.get_window_size()
        screen_width = screen_size["width"]
        screen_height = screen_size["height"]
        self.driver.swipe(screen_width * 1 / 2, screen_height * 3 / 4, screen_width * 1 / 2, screen_height * 1 / 4,
                          1000)
        sleep(5)

        # 테스트 제한 시간 5초 설정
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnTimerFive')
        el.click()
        sleep(3)

        # 테스트 시작 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnStartTest')
        el.click()
        sleep(2)

        # 1번문제 skip
        sleep(6)

        # 2번 문제 pass 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/textViewPass')
        el.click()
        sleep(2)

        # 3번 문제 1번째 선택지 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/ans1')
        el.click()
        sleep(2)

        # 4번 문제 2번째 선택지 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/ans2')
        el.click()
        sleep(2)

        # 5번 문제 3번째 선택지 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/ans3')
        el.click()
        sleep(2)

        # 테스트 완료 선택
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnTestFinish')
        el.click()
        sleep(4) # 컨텐츠 메인 이동 시간 확보

    def test_07_dayOneFullTest(self):
        # DAY 1 테스트 버튼 클릭
        contents = self.driver.find_elements(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnTest')
        contents[0].click()
        sleep(3)

        # 문제 개수 영역 선택 및 입력
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/questAmt')
        max_test_num = \
        str(self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/questAmt').text).split(" ")[1][:-1]
        el.send_keys(max_test_num)
        sleep(5)

        # 아래로 스크롤링 - element 노출을 위함
        screen_size = self.driver.get_window_size()
        screen_width = screen_size["width"]
        screen_height = screen_size["height"]
        self.driver.swipe(screen_width * 1 / 2, screen_height * 3 / 4, screen_width * 1 / 2, screen_height * 1 / 4,
                          1000)
        sleep(3)

        # 테스트 시작 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnStartTest')
        el.click()
        sleep(3)

        # 마지막 문제까지 skip 클릭
        for num in range(int(max_test_num)):
            el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/textViewPass')
            el.click()
            sleep(2)

        # 테스트 완료 선택
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnTestFinish')
        el.click()
        sleep(4) # 컨텐츠 메인 이동 시간 확보

    def test_08_testResultCheck(self):
        # 마이룸 이동
        wait = WebDriverWait(self.driver, 30)
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
        el.click()
        sleep(5)

        # 테스트 결과 페이지 진입
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value='com.etoos.app.wm:id/rowTestResult')
        el.click()
        sleep(5)

        # 테스트 결과 확인
        if int(self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/staticWordCount').text[:-1]) == 0:
            self.fail("테스트 결과가 저장되지 않았습니다.")


    # tearDown > 테스트 메서드 실행 후 호출되는 코드 / setUp이 성공한다면 테스트 성공 여부에 상관없이 실행
    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == '__main__':
    unittest.main() # 테스트 스크립트에 명령행 인터페이스 제공
