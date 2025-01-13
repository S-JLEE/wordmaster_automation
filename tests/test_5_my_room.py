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
    noReset = True
    # autoWebview=True # Webview context 전환 허용
)


class MYROOMFUNCTION(unittest.TestCase):

    # setUp > 1개의 테스트마다 자동으로 호출하는 사전 코드 / 실행 중 예외 사항 발생 시 테스트 메서드는 실행하지 않음
    def setUp(self):
        self.driver = webdriver.Remote(
            command_executor=appiumServerUrl, options=UiAutomator2Options().load_capabilities(capabilities))

    # 테스트 실행
    def test_01_moveMyroom(self):
        """
        Test Suite 4의 테스트 결과값이 필요하므로 noReset 값은 True로 고정
        :return:
        """
        # 마이룸 이동
        wait = WebDriverWait(self.driver, 30)
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
        el.click()
        sleep(5)

    def test_02_saveStudyData(self):
        # 변수 설정
        wait = WebDriverWait(self.driver, 30)
        screen_size = self.driver.get_window_size()

        # 학습데이터 저장 페이지 진입
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/rowSaveData')))
        el.click()
        sleep(5)

        # 학습데이터 저장 버튼 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnUpload')
        el.click()
        sleep(3)

        # Trouble Shooting - 화면 해상도로 인한 텍스트 미노출의 경우 방지 code -> swipe 동작으로 해결
        self.driver.swipe(screen_size["width"] * 0.5,
                          screen_size["height"] * 0.7,
                          screen_size["width"] * 0.5,
                          screen_size["height"] * 0.3,
                          duration=300)
        sleep(3)

        # 업로드 텍스트가 노출되지 않으면 fail처리
        if self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/saveHistory').text[-3:] != "업로드":
            self.fail("학습데이터 저장에 실패했습니다.")

        # 뒤로가기 클릭
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value='com.etoos.app.wm:id/btnBack')
        el.click()
        sleep(5)

        # 로그아웃 진행
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value='com.etoos.app.wm:id/btnLogout')
        el.click()
        sleep(3)
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value='com.etoos.app.wm:id/btnConfirm')
        el.click()
        sleep(3)

        # 로그인 진행
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom'))) # 마이룸 클릭
        el.click()
        sleep(10)  # 통합회원 로그인 화면 출력 시간 대기

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

        ### 컨텐츠 재다운로드
        # 학습관 클릭
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/nav_study_room")
        wait.until(EC.visibility_of(el))
        el.click()
        sleep(4)

        # 컨텐츠 다운로드
        buttons = self.driver.find_elements(by=AppiumBy.ID,
                                            value='com.etoos.app.wm:id/btnContentsAction')
        buttons[0].click()
        sleep(10)

        # 다운로드 진행 중일 경우 1초마다 다운로드 상태인지 확인
        try:
            while True:
                if self.driver.find_element(by=AppiumBy.ID,
                                            value='com.etoos.app.wm:id/progress') is False:
                    break
                else:
                    sleep(2)
        except NoSuchElementException:
            pass

        sleep(5)
        # 마이룸 재진입
        self.driver.activate_app(app_id='com.etoos.app.wm') #앱 종료하면 다시 on
        self.wait_for_app_foreground('com.etoos.app.wm', 10) # 앱이 실행 될 때까지 시도
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
        el.click()
        sleep(5)

        # 테스트 결과 페이지 진입
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value='com.etoos.app.wm:id/rowTestResult')
        el.click()
        sleep(5)

        # 테스트 조건 확인
        if int(self.driver.find_element(by=AppiumBy.ID,
                                        value='com.etoos.app.wm:id/staticWordCount').text[:-1]) == 0:
            self.fail("학습 데이터 복구에 실패했습니다.")

        # 마이룸 이동
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
        el.click()
        sleep(5)
    def test_03_deleteStudyData(self):
        # 변수 설정
        wait = WebDriverWait(self.driver, 30)
        # 학습데이터 초기화 페이지 이동
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/rowInitData')))
        el.click()
        sleep(5)

        # 학습데이터 초기화 버튼 클릭
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/btnInit')))
        el.click()
        sleep(3)

        # 삭제 버튼 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnConfirm')
        el.click()
        sleep(5)

        # (초기화 여부 확인) 테스트 결과 초기화 여부 확인
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/rowTestResult')))
        el.click()
        sleep(3)

        if self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnBooks').text != "테스트 데이터 없음":
            self.fail("학습 데이터 초기화에 실패했습니다.")

        # 마이룸 이동
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
        el.click()
        sleep(5)

    def test_04_alarmSettings(self):
        wait = WebDriverWait(self.driver, 30)
        # 알림 설정 페이지 진입
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/rowPush')))
        el.click()
        sleep(5)

        # 푸시 알림 설정 변경 > 시스템 설정에서도 변경
        push_buttons = self.driver.find_elements(by=AppiumBy.ID, value='com.etoos.app.wm:id/rowIcon')
        push_buttons[0].click()
        sleep(3)

        # 시스템 설정으로 이동
        el = self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnConfirm')
        el.click()
        sleep(3)

        # 시스템 설정 > 알림 토글 버튼 클릭
        el = self.driver.find_element(by=AppiumBy.ID, value='com.android.settings:id/switch_widget')
        el.click()
        sleep(3)

        # 워드마스터 앱 복귀
        self.driver.activate_app(app_id='com.etoos.app.wm')
        sleep(3)

        # 마케팅 알림 설정 변경 > toggle button 동작 확인
        push_buttons = self.driver.find_elements(by=AppiumBy.ID, value='com.etoos.app.wm:id/rowIcon')
        push_buttons[1].click()
        sleep(2)
        push_buttons[1].click()
        sleep(2)

        # 마이룸 이동
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/nav_myroom')))
        el.click()
        sleep(5)

    def test_05_accountWebview(self):
        wait = WebDriverWait(self.driver, 30)
        # 통합회원 관리 페이지 진입
        el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/etoosMemberSetting')))
        el.click()
        sleep(10)  # webview element 활성화 대기 시간

        if self.driver.find_element(by=AppiumBy.ID, value='com.etoos.app.wm:id/webViewContainer'):
            sleep(5)
            el = wait.until(EC.visibility_of_element_located((AppiumBy.ID, 'com.etoos.app.wm:id/btnBack')))
            el.click()
            sleep(5)
        else:
            self.fail("통합회원 관리 페이지 로딩에 실패했습니다.")


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
