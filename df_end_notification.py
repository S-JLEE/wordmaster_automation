"""
결과 알림 code
1. arn 순서: project ARN > run ARN > job ARN(특정 기기) > suite ARN (test specification log 접근 가능)
2. 필요 데이터: 기기명, 테스트 결과 (ok수 / error수 = fail 수)
3. Bigquery의
"""
import boto3
import pandas as pd
import json
import requests
import datetime
from zoneinfo import ZoneInfo
import logging
import sys
from google.oauth2 import service_account
from google.cloud import bigquery

# Alarm creation
def webhookSender(text):
    webhook_url = "https://mm.etoos.com/hooks/438rqq34utykzjz91eoh39bcmy"
    message = {
        "text": f"{text}"
    }
    try:
        response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            logging.info('Notification sent successfully')
            return {
                'statusCode': 200,
                'body': json.dumps('Notification sent successfully')
            }
        else:
            logging.error(f"Failed to send notification, status code: {response.status_code}, response: {response.text}")
            return {
                'statusCode': response.status_code,
                'body': json.dumps('Failed to send notification')
            }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending notification: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error sending notification: {e}")
        }

# Initialize AWS Device Farm client
def create_device_farm_client(access_key_id, secret_access_key, region_name='us-west-2'):
    # Initialize AWS Device Farm client
    return boto3.client(
        'devicefarm',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )

# Get list of projects in device farm (1 depth)
def list_device_farm_projects(client):
    """ List all projects in AWS Device Farm """
    try:
        projects = []
        paginator = client.get_paginator('list_projects')
        for page in paginator.paginate():
            projects.extend(page['projects'])
        return projects
    except Exception as e:
        print(f"An error occurred while listing projects: {e}")
        return []

# Get list of the runs in project (2 depth)
def list_runs(client, project_arn):
    """ List all runs for a given project """
    try:
        runs = []
        paginator = client.get_paginator('list_runs')
        for page in paginator.paginate(arn=project_arn):
            runs.extend(page['runs'])
        return runs
    except Exception as e:
        print(f"An error occurred while listing runs: {e}")
        return []

# Get list of the jobs in run (3 depth)
def list_jobs(client, run_arn):
    try:
        jobs = []
        paginator = client.get_paginator('list_jobs')
        for page in paginator.paginate(arn=run_arn):
            jobs.extend(page['jobs'])
        return jobs
    except Exception as e:
        print(f"An error occurred while listing runs: {e}")
        return []

# Get list of the suites in job (4 depth)
def list_suites(client, job_arn):
    try:
        suites = []
        paginator = client.get_paginator('list_suites')
        for page in paginator.paginate(arn=job_arn):
            suites.extend(page['suites'])
        return suites
    except Exception as e:
        print(f"An error occurred while listing runs: {e}")
        return []

# Get list of tests in suite (5 depth)
def list_tests(client, suite_arn):
    try:
        tests = []
        paginator = client.get_paginator('list_tests')
        for page in paginator.paginate(arn=suite_arn):
            tests.extend(page['tests'])
        return tests
    except Exception as e:
        print(f"An error occurred while listing runs: {e}")
        return []

# Get list of the artifacts in jobs
def list_artifacts(client, arn, type):
    try:
        artifacts = []
        paginator = client.get_paginator('list_artifacts')
        for page in paginator.paginate(arn=arn, type=type):
            artifacts.extend(page['artifacts'])
        return artifacts
    except Exception as e:
        logging.error(f"An error occurred while listing artifacts: {e}")
        return []

# Setting Credentials
# AWS
aws_access_key = pd.read_csv("./credentials/ZE231204_accessKeys.csv")
ACCESS_KEY_ID = aws_access_key["Access key ID"][0]
SECRET_ACCESS_KEY = aws_access_key["Secret access key"][0]

# Google Bigquery
credential_path = 'credentials/etoos-automation-2370e7d11ce8.json'
credentials = service_account.Credentials.from_service_account_file(credential_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#################
# Code Initialize
#################
if __name__ == "__main__":
    # google Bigquery의 TASK_COMPLETE 열 체크
    # Define the query to check if all values in 'TASK_COMPLETE' are TRUE
    query = """
    SELECT COUNT(*) AS not_true_count
    FROM `etoos-automation.Wordmaster_automation_DB.login_info`
    WHERE NOT TASK_COMPLETE OR TASK_COMPLETE IS NULL
    """

    # Run the query
    query_job = client.query(query)

    # Wait for the query to finish
    results = query_job.result()

    # Check the results
    for row in results:
        if row.not_true_count > 0:
            print("일부 작업이 미완료 상태입니다...... 해당 JOB의 테스트를 종료합니다.")
            sys.exit() # TASK_COMPLETE 행이 전부 TRUE 값이 아니면 drop
        else:
            # TASK_COMPLETE 행이 전부 TRUE 값이면 코드 이어서 실행
            print("모든 작업이 완료 되었습니다. 데이터 읽는 중......")

    client = create_device_farm_client(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
    print("Listing all projects in AWS Device Farm:")

    # Project 리스트 불러오기
    projects = list_device_farm_projects(client)
    # fetch project arn and project name
    for project in projects:
        # 라이브 버전: Wordmaster_live
        # 테스트 버전: Wordmaster_test
        if project['name'] == "Wordmaster_live":
            live_project = project
    project_arn = live_project['arn'] # 프로젝트 명이 Wordmaster_live의 arn 정보 저장 > run arn을 찾는데 사용
    project_name = live_project['name']

    # Run data 불러오기
    runs = list_runs(client, project_arn)
    current_run = runs[0]
    run_arn = current_run['arn'] # 가장 최근에 생성한 run의 arn 정보 저장 > job arn을 찾는데 사용

    # run > job 중 status가 COMPLETED 인 job의 arn 정보 획득
    jobs = list_jobs(client, run_arn)

    # list for saving data
    device_name = []
    num_ok = []
    num_ERROR = []
    video_url = []
    fail_log = []

    for job in jobs:
        error_text = []
        # make database of each job information
        job_arn = job['arn'] # suite arn 확인에 사용

        # device name 수집
        d_name = job['device']['name']
        device_name.append(d_name)

        # test 별 pass / fail 데이터 수집
        logs = list_artifacts(client, job_arn, 'FILE')
        for log in logs:
            if log['type'] == "TESTSPEC_OUTPUT":
                output_url = log['url'] # TESTSPEC 결과 url 불러오기
                output_result = requests.get(output_url)
                if output_result.status_code == 200:
                    output_content = output_result.text # url의 text 파일 불러오기
                else:
                    print(f"Failed to retrieve the file: Status code {output_result.status_code}")
                    output_content = ""
                # 로그 txt 파일 내 ok 수 / ERROR 수 읽기
                if output_content:
                    ok_count = 0
                    ERROR_count = 0
                    if isinstance(output_content, str):
                        output_content = output_content.splitlines()
                    for line in output_content:
                        if '... ok' in line:
                            ok_count += 1
                        elif '... FAIL' in line:
                            ERROR_count += 1
                        elif '... ERROR' in line:
                            ERROR_count += 1
                            err_log = line
                            error_text.append(err_log)
                    num_ok.append(ok_count)
                    num_ERROR.append(ERROR_count)
                    fail_log.append(error_text)
            # # 테스트 영상 다운로드 링크 저장
            # elif log['type'] == "VIDEO":
            #     vid_url = log['url'] # 테스트 영상 다운로드 url 불러오기
            #     video_url.append(vid_url)

    # Create json data for the alarm
    result_data = [
        {
            "name": device_name[i],
            "num_success": num_ok[i],
            "num_fail": num_ERROR[i],
            "fail_log": fail_log[i]
            #"video_url": video_url[i]
        }
        for i in range(len(device_name))
    ]
    result_json = json.dumps(result_data, indent=4) # json 문자열
    parsed_json = json.loads(result_json) # json 문자열을 python 객체로 변환

    ##########
    # 알림 전송
    ##########
    # Set up
    korea_timezone = ZoneInfo("Asia/Seoul")
    current_time = datetime.datetime.now(korea_timezone)
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M') # 시간 형식으로 변경

    ##########
    # 메시지 생성 (테스트 생성 시간 추가 / 총 소요 시간 추가)
    ##########
    context_main = [
        ":bell: **워드마스터(Live) 기본 기능 테스트가 완료되었습니다.**",
        f":alarm_clock: **_테스트 완료 시간_**: {formatted_time}",
        f"",
        "",
        "---"
    ]
    for entry in parsed_json:
        fail_log_str = "\n".join(entry['fail_log']) if entry['fail_log'] else '없음'
        device_info = [
            f"**기기 명**: {entry['name']}",
            f":white_check_mark: **PASS 수**: {entry['num_success']}",
            f":no_entry: **FAIL 수**: {entry['num_fail']}",
            f"**Fail 로그**: {fail_log_str}",
            # f"**테스트 영상**: [다운로드 링크]({entry['video_url']})",
            "",
            "",
            "---"
        ]
        context_main.extend(device_info)
    message_context = "\n".join(context_main)

    # 메시지 전송
    webhookSender(message_context)
