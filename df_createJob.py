import boto3
import datetime
import pandas as pd

# AWS 자격 증명 설정 / 자격 증명 관련된 내용은 인프라팀에 문의
aws_access_key = pd.read_csv("/Users/etoos/Desktop/Documents/Etoos/Project/automation/wordmaster/device_farm/wordmaster/LIVE/credentials/ZE231204_accessKeys.csv") # Access key 파일의 절대 경로 삽입
aws_access_key_id = aws_access_key["Access key ID"][0]
aws_secret_access_key = aws_access_key["Secret access key"][0]
region_name = 'us-west-2'  # Device Farm 서비스가 있는 AWS 지역 (고정)

# Device Farm 클라이언트 생성
devicefarm = boto3.client('devicefarm',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=region_name)

"""
Device farm 의 Wordmaster_test project용 코드 입니다. Wordmaster_live 사용을 위해서는 일부 수정이 필요합니다.
"""
def get_project_arn(client):
    """ List all projects in AWS Device Farm """
    try:
        projects = []
        paginator = client.get_paginator('list_projects')

        # get the list of projects from the client
        for page in paginator.paginate():
            projects.extend(page['projects'])

        # get project arn
        for project in projects:
            if project['name'] == "Wordmaster_live": # 수정사항 1. Wordmaster_test / Wordmaster_live
                project_arn = project['arn']

        return project_arn
    except Exception as e:
        print(f"An error occurred while listing projects: {e}")
        return []

# search uploads arn (test_spec, test_package, app)
def get_uploads_arn(project_arn):
    """ List all uploads in AWS Device Farm in project"""
    try:
        response = devicefarm.list_uploads(
            arn=project_arn
        )
        # print(response["uploads"]) # project arn에 해당하는 전체 api 결과 확인
        list_package_arn = []
        list_spec_arn = []
        list_app_arn = []
        for element in response["uploads"]:
            if element['type'] == 'APPIUM_PYTHON_TEST_PACKAGE':
                api_result = {
                    "arn": element['arn'],
                    "created": element['created'],
                    "name": element['name']
                }
                # print(api_result) # python test package api 결과 확인
                list_package_arn.append(api_result)
            elif element['type'] == 'APPIUM_PYTHON_TEST_SPEC':
                api_result = {
                    "arn": element['arn'],
                    "created": element['created'],
                    "name": element['name']
                }
                # print(api_result) # test spec api 결과 확인
                list_spec_arn.append(api_result)
            elif element['type'] == 'ANDROID_APP':
                api_result = {
                    "arn": element['arn'],
                    "created": element['created'],
                    "name": element['name']
                }
                # print(api_result) # app api 결과 확인
                list_app_arn.append(api_result)
            else:
                continue
        latest_package = max(list_package_arn, key=lambda x: x['created']) # get the latest uploaded package arn
        latest_spec = max(list_spec_arn, key=lambda x: x['created']) # get the latest uploaded spec arn
        latest_app = max(list_app_arn, key=lambda x: x['created']) # get the latest uploaded app arn

        package_arn = latest_package['arn']
        spec_arn = latest_spec['arn']
        app_arn = latest_app['arn']

        print(package_arn, spec_arn, app_arn, sep="\n") # 함수 실행 결과물 점검용

        return package_arn, spec_arn, app_arn
    except Exception as e:
        print(f"An error occurred while listing projects: {e}")
        return []

# Device Pool 정보 나열
def list_device_pools(project_arn):
    try:
        response = devicefarm.list_device_pools(
            arn=project_arn
        )

        for pool in response['devicePools']:
            if pool['name'] == "test_device_pool": # 수정 사항 2. project에 생성한 device pool 기입
                pool_arn = pool['arn']
        return pool_arn
    except Exception as e:
        print(f"Error listing device pools: {e}")

def create_devicefarm_run(device_pool_arn, package_arn, spec_arn, app_arn):
    try:
        # 오늘의 날짜를 기반으로 실행 이름 생성
        run_name = f"Daily_Run_{datetime.datetime.now().strftime('%Y%m%d')}"

        # 테스트 실행 생성
        response = devicefarm.schedule_run(
            projectArn=project_arn,
            appArn=app_arn,
            devicePoolArn=device_pool_arn,
            name=run_name,
            test={
                'type': 'APPIUM_PYTHON',  # 테스트 유형 (고정)
                'testPackageArn': package_arn,
                'testSpecArn': spec_arn
            }
        )

        print(f"Test run created: {response['run']['arn']}")
    except Exception as e:
        print(f"Error creating test run: {e}")

if __name__ == '__main__':
    """Device Farm 프로젝트 및 Device Pool ID 설정"""

    project_arn = get_project_arn(client=devicefarm)  # get project ARN (wordmaster test)
    package_arn, spec_arn, app_arn = get_uploads_arn(project_arn) # get the latest arns for the devicefarm
    device_pool_arn = list_device_pools(project_arn) # get device pool for the test

    # 새로운 테스트 실행을 생성
    create_devicefarm_run(device_pool_arn, package_arn, spec_arn, app_arn)
