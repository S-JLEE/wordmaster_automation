from google.oauth2 import service_account
from google.cloud import bigquery
from time import sleep
import json
import random

# 계정 분리를 위한 난수 생성 함수
def generate_random_number():
    max_iter = random.randint(3, 10)
    num_iter = 0
    random_num = 0

    while num_iter < max_iter:
        random_function = random.choice([random.randint, random.uniform])

        if random_function == random.randint:
            # Generate a random integer within a specified range
            value = random_function(2, 4)
        elif random_function == random.uniform:
            # Generate a random float within a specified range
            value = random_function(2, 4)

        random_num += value
        num_iter += 1

    return random_num

# 1. Generate random number for wait
random_number = generate_random_number()
print(f"time to sleep for {round(random_number * 2, 2)} second ")
sleep(random_number * 2)

credential_path = 'credentials/etoos-automation-2370e7d11ce8.json'
credentials = service_account.Credentials.from_service_account_file(credential_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# 2. Get account information from Google Bigquery
query = '''
SELECT *
FROM `etoos-automation.Wordmaster_automation_DB.login_info`;
'''
job = client.query(query) # API request
login_df = job.to_dataframe() # Bigquery에서 가져온 내용을 data frame에 저장

for num in range(0, len(login_df)):
    if login_df.iloc[num].AVAILABILITY == True:
        index = num
        test_id = login_df.iloc[num].ID
        test_pw = login_df.iloc[num].PW
        print(f"index: {index}", f"id: {test_id}", f"pw:{test_pw}")
        query = f'''
        UPDATE `etoos-automation.Wordmaster_automation_DB.login_info`
        SET AVAILABILITY = FALSE
        WHERE ID = @test_id AND PW = @test_pw
        '''
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("test_id", "STRING", test_id),
                bigquery.ScalarQueryParameter("test_pw", "STRING", test_pw)
            ]
        )
        result = client.query(query, job_config=job_config)
        print(f"Updated AVAILABILITY to False for row where \n\n ID='{test_id}' and PW='{test_pw}'.")
        break # test_id, test_pw 값을 얻으면 해당 row의 availability 값을 false로 전환하고 loop 탈출
    else:
        print("Following Account is already been occupied..")

account_info = {
    "test_id": test_id,
    "test_pw": test_pw
}

# Save test_id and test_pw to account.json
with open('account.json', 'w') as json_file:
    json.dump(account_info, json_file)

print("Test ID and password saved to account.json.")



