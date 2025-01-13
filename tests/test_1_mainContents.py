import unittest
import json
from time import sleep
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


class appHomeContents(unittest.TestCase):

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

    def test_02_highContentsSwipe(self):

        # App 실행 대기
        sleep(10)

        # 스크린 이동 기준 변수 처리
        screen_size = self.driver.get_window_size()
        num_swipe = 8

        ele_location = self.driver.find_element(by=AppiumBy.ID,
                                                value="com.etoos.app.wm:id/highSchoolContentsTitle").location
        # 고등 스와이핑 영역 제목을 위로 이동
        self.driver.swipe(ele_location['x'],  # from x
                          ele_location['y'],  # from y
                          ele_location['x'],  # to x
                          screen_size["height"] * 0.3,  # to y
                          1000)
        sleep(4)

        ## 우측으로 스와이핑
        # 기준점 체크
        ele_location = self.driver.find_element(by=AppiumBy.ID,
                                                value="com.etoos.app.wm:id/highSchoolContentsRecycler").location
        ele_size = self.driver.find_element(by=AppiumBy.ID,
                                            value="com.etoos.app.wm:id/highSchoolContentsRecycler").size
        # 스와이핑 동작 실행
        for i in range(num_swipe):
            self.driver.swipe(screen_size["width"] * 0.7,  # from x
                              ele_location['y'] + (ele_size['height'] * 0.5),  # from y
                              screen_size["width"] * 0.3,  # to x
                              ele_location['y'] + (ele_size['height'] * 0.5),  # to y
                              300)
        sleep(4)

    def test_03_highContentsCheck(self):
        screen_size = self.driver.get_window_size()
        num_swipe = 8
        # [+] 버튼 클릭 > 고등 전체 콘텐츠 이동
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/btnPlusHighSchool")
        el.click()
        sleep(3)

        # 아래로 스와이핑
        for i in range(num_swipe):
            self.driver.swipe(screen_size["width"] * 0.5,  # from x
                              screen_size["height"] * 0.7,  # from y
                              screen_size["width"] * 0.5,  # to x
                              screen_size["height"] * 0.3,  # to y
                              300)
        sleep(3)

        # 샘플 컨텐츠 상세 페이지
        button_group = self.driver.find_elements(by=AppiumBy.ID,
                                       value="com.etoos.app.wm:id/btnViewDetail")
        if button_group:
            button_group[0].click() # 1번째 상세 보기 버튼 클릭
            sleep(4) # 페이지 노출 대기
        else:
            print("고등 컨텐츠 미노출")

    def test_04_backToMain(self):
        # 뒤로가기 * 2
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/btnBack")
        el.click()
        sleep(4)

        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/btnBack")
        el.click()
        sleep(3)


    def test_05_midContentsMove(self):
        # 중등 컨텐츠를 중앙으로 이동
        screen_size = self.driver.get_window_size()
        ele_location = self.driver.find_element(by=AppiumBy.ID,
                                                value="com.etoos.app.wm:id/midSchoolContentsTitle").location
        self.driver.swipe(ele_location['x'],  # from x
                          ele_location['y'],  # from y
                          ele_location['x'],  # to x
                          screen_size["height"] * 0.4,  # to y
                          2000)
        sleep(3)

    def test_06_midContentsCheck(self):
        screen_size = self.driver.get_window_size()
        num_swipe = 4
        # [+] 버튼 클릭
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/btnPlusMidSchool")
        el.click()
        sleep(4)

        # 아래로 스와이핑 + 전체 컨텐츠 노출 확인
        for i in range(num_swipe):
            self.driver.swipe(screen_size["width"] * 0.5,  # from x
                              screen_size["height"] * 0.7,  # from y
                              screen_size["width"] * 0.5,  # to x
                              screen_size["height"] * 0.3,  # to y
                              300)
        sleep(4)

        # 샘플 컨텐츠 상세 페이지
        button_group = self.driver.find_elements(by=AppiumBy.ID,
                                                 value="com.etoos.app.wm:id/btnViewDetail")
        if button_group:
            button_group[0].click()  # 1번째 상세 보기 버튼 클릭
            sleep(4)  # 페이지 노출 대기
        else:
            print("중등 컨텐츠 미노출")

    def test_07_backToMain(self):
        # 뒤로가기
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/btnBack")
        el.click()
        sleep(4)

        # 홈 이동
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/nav_home")
        el.click()
        sleep(3)

    def test_08_elemContentsMove(self):
        screen_size = self.driver.get_window_size()
        num_swipe = 7
        for i in range(num_swipe):
            self.driver.swipe(screen_size["width"] * 0.5,  # from x
                              screen_size["height"] * 0.7,  # from y
                              screen_size["width"] * 0.5,  # to x
                              screen_size["height"] * 0.3,  # to y
                              300)
        sleep(5)

    def test_09_elemContentsCheck(self):
        # [+] 버튼 클릭
        el = self.driver.find_elements(by=AppiumBy.ID, value='com.etoos.app.wm:id/btnShowMore')
        el[0].click()
        sleep(5)

        # 샘플 컨텐츠 상세 페이지
        button_group = self.driver.find_elements(by=AppiumBy.ID,
                                                 value="com.etoos.app.wm:id/btnViewDetail")
        if button_group:
            button_group[0].click()  # 1번째 상세 보기 버튼 클릭
            sleep(5)  # 페이지 노출 대기
        else:
            print("초등 컨텐츠 미노출")

    def test_10_backToMain(self):
        # 뒤로가기
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/btnBack")
        el.click()
        sleep(5)

        # 홈 이동
        el = self.driver.find_element(by=AppiumBy.ID,
                                      value="com.etoos.app.wm:id/nav_home")
        el.click()
        sleep(3)


    # tearDown > 테스트 메서드 실행 후 호출되는 코드 / setUp이 성공한다면 테스트 성공 여부에 상관없이 실행
    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == '__main__':
    unittest.main() # 테스트 스크립트에 명령행 인터페이스 제공
