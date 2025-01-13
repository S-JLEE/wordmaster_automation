from google.oauth2 import service_account
from google.cloud import bigquery
import time

credential_path = 'credentials/etoos-automation-2370e7d11ce8.json'
credentials = service_account.Credentials.from_service_account_file(credential_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)


# QUERY - reset availability to TRUE
query1 = f'''
UPDATE `etoos-automation.Wordmaster_automation_DB.login_info`
SET AVAILABILITY = TRUE
WHERE ID is not NULL ;
'''

# QUERY - set task complete to true
query2 = f'''
UPDATE `etoos-automation.Wordmaster_automation_DB.login_info`
SET TASK_COMPLETE = FALSE
WHERE ID is not NULL ;
'''

# availability 초기화
job = client.query(query1)  # API request
job.result()  # Wait for the query to complete

# 테스트 완료된 ID의 task_complete 값 변경
job = client.query(query2)  # API request
job.result()  # Wait for the query to complete

# 쿼리 정보 업데이트 시간 확보
time.sleep(3)

print("Successfully updated account query.")
print("작업 내용= AVAILABILITY: TRUE / TASK_COMPLETE: FALSE")
