from google.oauth2 import service_account
from google.cloud import bigquery
import json
import time

credential_path = 'credentials/etoos-automation-2370e7d11ce8.json'
credentials = service_account.Credentials.from_service_account_file(credential_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# 1. read data - account.json
json_filepath = './account.json'
with open(json_filepath, 'r') as file:
    data = json.load(file)

test_id = data["test_id"]

# 2. QUERY - reset availability to TRUE
query1 = f'''
UPDATE `etoos-automation.Wordmaster_automation_DB.login_info`
SET AVAILABILITY = TRUE
WHERE ID = '{test_id}' ;
'''

# 3. QUERY - set task complete to true
query2 = f'''
UPDATE `etoos-automation.Wordmaster_automation_DB.login_info`
SET TASK_COMPLETE = TRUE
WHERE ID = '{test_id}' ;
'''

# availability 초기화
job = client.query(query1)  # API request
job.result()  # Wait for the query to complete

# 테스트 완료된 ID의 task_complete 값 변경
job = client.query(query2)  # API request
job.result()  # Wait for the query to complete

# 쿼리 정보 업데이트 시간 확보
time.sleep(3)

print("Update query executed successfully.")