import requests
import sys
import csv
import os
import io

from azure.storage.blob import BlockBlobService
from io import BytesIO




class config():
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session.auth = self.email , self.password
        self.url = 'https://olinqua.zendesk.com/api/v2/'
        self.account_name = 'devblobdatazendesk'
        self.account_key = 'Ve77nc2T1Ieo0xGhzb86OBTPFM8L5KTGZkpQ4PAqdgrEpNx9Ej7VqZEc6Giemsf+hXriYK8xKMSonVP7REJUFQ=='
        self.file_path = "C:/Users/phamm.DRITZII/Documents/GitHub/webscrapping/zendesk_api/"
        self.delimiter = ','
        self.quote = '"'
        self.quote_normals = csv.QUOTE_NONNUMERIC
        try:
            self.response = self.session.get(self.url)
            if self.response.status_code != 200:
                print("Not able to login", sys.stderr)
            else:
                print("Login Success",sys.stderr)
        except TimeoutError as err:
            print(err,sys.stderr)
    def get_all_tickets(self):
        try:
            typename = 'tickets'
            test = self.session.get(self.url + typename + '.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                    writer.writerow(['status','type','external_id','recipient','requester_id','submitter_id',
                    'assignee_id','organization_id','has_incidents','url','id','created_at','subject',
                    'priority','via_channel','via_source_from','via_source_to','via_source_rel','custom_fields',
                    'raw_subject','description','collaborator_ids','follower_ids','email_cc_ids','forum_topic_id',
                    'problem_id','is_public','due_at','tags'])
                    url = self.url + typename + '.json'
                    while url:
                        data = self.session.get(url).json()
                        for each in data[typename]:
                            writer.writerow([each['status'],
                                            each['type'],
                                            each['external_id'],
                                            each['recipient'],
                                            each['requester_id'],
                                            each['submitter_id'],
                                            each['assignee_id'],
                                            each['organization_id'],
                                            each['has_incidents'],
                                            each['url'],
                                            each['id'],
                                            each['created_at'],
                                            each['subject'],
                                            each['priority'],
                                            each['via']['channel'],
                                            each['via']['source']['from'],
                                            each['via']['source']['to'],
                                            each['via']['source']['rel'],
                                            each['custom_fields'],
                                            each['raw_subject'],
                                            each['description'],
                                            each['collaborator_ids'],
                                            each['follower_ids'],
                                            each['email_cc_ids'],
                                            each['forum_topic_id'],
                                            each['problem_id'],
                                            each['is_public'],
                                            each['due_at'],
                                            each['tags']])
                        url = data['next_page']
                        print(url)
                print("connecting to blob storage")
                blob_service = BlockBlobService(account_name = self.account_name,account_key = self.account_key)
                blob_service.create_blob_from_path('csv-blob', blob_name=typename + '.csv',file_path=self.file_path + typename + '.csv')
                generator = blob_service.list_blobs('csv-blob')
                for blob in generator:
                    print("\t Blob name: " + blob.name)
            else:
                print("Not Successful",sys.stderr)
                return False
        except UnicodeEncodeError as e:
            print(e,sys.stderr)
    def get_incremental_ticket(self,unix_time):
        try:
            typename = 'incremental_tickets'
            data = self.session.get(self.url + 'incremental/tickets.json?per_page=1000&start_time={}'.format(str(unix_time)))
            if data.status_code in [200,'200']:
                print("Successful Call")
                with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                    writer.writerow(['url','id','external_id','via_channel','via_source_from','via_source_to',
                    'via_source_rel','created_at','updated_at','type','subject','raw_subject','description',
                    'priority','status','recipient','requester_id','submitter_id','assignee_id',
                    'organization_id','group_id','collaborator_ids','follower_ids','email_cc_ids','forum_topic_id',
                    'problem_id','has_incidents','is_public','due_at','tags','custom_fields','satisfaction_rating','sharing_agreement_ids','fields',
                    'followup_ids','brand_id','allow_channelback','allow_attachments','generated_timestamp'])
                    end_of_stream = False
                    while end_of_stream is not True:
                        old = self.session.get(self.url + 'incremental/tickets.json?per_page=1000&start_time=1332034771').json()
                        for each in old['tickets']:
                            writer.writerow([each['url'],
                                                each['id'],
                                                each['external_id'],
                                                each['via']['channel'],
                                                each['via']['source']['from'],
                                                each['via']['source']['to'],
                                                each['via']['source']['rel'],
                                                each['created_at'],
                                                each['updated_at'],
                                                each['type'],
                                                each['subject'],
                                                each['raw_subject'],
                                                each['description'],
                                                each['priority'],
                                                each['status'],
                                                each['recipient'],
                                                each['requester_id'],
                                                each['submitter_id'],
                                                each['assignee_id'],
                                                each['organization_id'],
                                                each['group_id'],
                                                each['collaborator_ids'],
                                                each['follower_ids'],
                                                each['email_cc_ids'],
                                                each['forum_topic_id'],
                                                each['problem_id'],
                                                each['has_incidents'],
                                                each['is_public'],
                                                each['due_at'],
                                                each['tags'],
                                                each['custom_fields'],
                                                each['satisfaction_rating'],
                                                each['sharing_agreement_ids'],
                                                each['fields'],
                                                each['followup_ids'],
                                                each['brand_id'],
                                                each['allow_channelback'],
                                                each['allow_attachments'],
                                                each['generated_timestamp']])
                        print(end_of_stream)                       
                        end_of_stream = old['end_of_stream']
                        old = old['next_page']
                        
            else:
                print("Not Successful",sys.stderr)
        except Exception as e:
            print(e,sys.stderr)
    def test_post_service(self):
        try:
            body = "{\"ticket\": {\"subject\": \"My printer is on fire!\", \"comment\": { \"body\": \"The smoke is very colorful.\"}}}"
            headers= {"Content-Type": "application/json"}
            data = self.session.post(self.url + 'tickets.json',data = body,headers=headers)
            if data.status_code in [201,'201']:
                print("Successful Call")
                print(data.content)
            else:
                print("Not Successful",sys.stderr)
                print(data.content)
                return False
        except Exception as e:
            print(e,sys.stderr)
    def test_get_service(self):
        try:
            test = self.session.get(self.url + 'ticket_audits.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                print(test.content)
                
            else:
                print("not working")
        except Exception as e:
            print(e,sys.stderr) 
    def get_groups(self):
        try:
            typename = 'groups'
            test = self.session.get(self.url + typename + '.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                    writer.writerow(['url','id','name','description','default','deleted','created_at',
                    'updated_at'])
                    url = self.url + typename + '.json'
                    while url:
                        old_url = self.session.get(url).json()
                        for each in old_url[typename]:
                            writer.writerow([each['url'],
                                            each['id'],
                                            each['name'],
                                            each['description'],
                                            each['default'],
                                            each['deleted'],
                                            each['created_at'],
                                            each['updated_at']])
                        url = old_url['next_page']
                        print(url)
                print("connecting to blob storage")
                blob_service = BlockBlobService(account_name = self.account_name,account_key = self.account_key)
                blob_service.create_blob_from_path('csv-blob', blob_name=typename + '.csv',file_path=self.file_path + typename + '.csv')
                generator = blob_service.list_blobs('csv-blob')
                for blob in generator:
                    print("\t Blob name: " + blob.name)
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)
    def get_activities(self): ### todo
        try:
            typename = 'activities'
            test = self.session.get(self.url + typename + '.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                    writer.writerow(['url','id','title','verb','user_id','actor_id','updated_at',
                    'created_at','object','target','notes','group_id',
                    'active_support_entitlement','premium_support_customer','support_end_date'])
                    url = self.url + typename + '.json'
                    while url:
                        old_url = self.session.get(url).json()
                        for each in old_url[typename]:
                            writer.writerow([each['url'],
                                            each['id'],
                                            each['title'],
                                            each['verb'],
                                            each['user_id'],
                                            each['actor_id'],
                                            each['updated_at'],
                                            each['created_at'],
                                            each['object']['comment']['value'],
                                            each['organization_fields']['support_end_date']])
                        url = old_url['next_page']
                        print(url)
                print("connecting to blob storage")
                blob_service = BlockBlobService(account_name = self.account_name,account_key = self.account_key)
                blob_service.create_blob_from_path('csv-blob', blob_name=typename + '.csv',file_path=self.file_path + typename + '.csv')
                generator = blob_service.list_blobs('csv-blob')
                for blob in generator:
                    print("\t Blob name: " + blob.name)
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)    
    def get_orgs(self):
        try:
            typename = 'organizations'
            test = self.session.get(self.url + typename + '.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                    writer.writerow(['url','id','name','shared_tickets','shared_comments','external_id','created_at',
                    'updated_at','domain_names','details','notes','group_id',
                    'active_support_entitlement','premium_support_customer','support_end_date'])
                    url = self.url + typename + '.json'
                    while url:
                        old_url = self.session.get(url).json()
                        for each in old_url[typename]:
                            writer.writerow([each['url'],
                                            each['id'],
                                            each['name'],
                                            each['shared_tickets'],
                                            each['shared_comments'],
                                            each['external_id'],
                                            each['created_at'],
                                            each['updated_at'],
                                            each['domain_names'],
                                            each['details'],
                                            each['notes'],
                                            each['group_id'],
                                            each['organization_fields']['active_support_entitlement'],
                                            each['organization_fields']['premium_support_customner'],
                                            each['organization_fields']['support_end_date']])
                        url = old_url['next_page']
                        print(url)
                print("connecting to blob storage")
                blob_service = BlockBlobService(account_name = self.account_name,account_key = self.account_key)
                blob_service.create_blob_from_path('csv-blob', blob_name=typename + '.csv',file_path=self.file_path + typename + '.csv')
                generator = blob_service.list_blobs('csv-blob')
                for blob in generator:
                    print("\t Blob name: " + blob.name)
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)
    def get_users(self):
        try:
            typename = 'users'
            test = self.session.get(self.url + typename + '.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                    writer.writerow(['id','url','name','email','created_at','updated_at','time_zone'])
                    url = self.url + typename + '.json'
                    while url:
                        old_url = self.session.get(url).json()
                        for each in old_url[typename]:
                            writer.writerow([each['id'],
                                            each['url'],
                                            each['name'],
                                            each['email'],
                                            each['created_at'],
                                            each['updated_at'],
                                            each['time_zone']])
                        url = old_url['next_page']
                        print(url)
                print("connecting to blob storage")
                blob_service = BlockBlobService(account_name = self.account_name,account_key = self.account_key)
                blob_service.create_blob_from_path('csv-blob', blob_name=typename + '.csv',file_path=self.file_path + typename + '.csv')
                generator = blob_service.list_blobs('csv-blob')
                for blob in generator:
                    print("\t Blob name: " + blob.name)
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)
    def get_ticket_metrics(self):
        try:
            typename = 'ticket_metrics'
            test = self.session.get(self.url + typename + '.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                    writer.writerow(['url','id','ticket_id','created_at','updated_at','group_stations','reopens',
                    'replies','assignee_updated_at','requester_updated_at','status_updated_at','initially_assigned_at',
                    'assigned_at','solved_at','latest_comment_added_at',
                    'reply_time_in_minutes','reply_time_in_minutes_business','first_resolution_time_in_minutes_calendar',
                    'first_resolution_time_in_minutes_business','full_resolution_time_in_minutes_calender',
                    'full_resolution_time_in_minutes_business','agent_wait_time_in_minutes_calender','agent_wait_time_in_minutes_business',
                    'requester_wait_time_in_minutes_calender','requester_wait_time_in_minutes_business','on_hold_time_in_minutes_calendar',
                    'on_hold_time_in_minutes_business','assignee_stations'])
                    url = self.url + typename + '.json'
                    while url:
                        old_url = self.session.get(url).json()
                        for each in old_url[typename]:
                            writer.writerow([each['url'],
                                            each['id'],
                                            each['ticket_id'],
                                            each['created_at'],
                                            each['updated_at'],
                                            each['group_stations'],
                                            each['reopens'],
                                            each['replies'],
                                            each['assignee_updated_at'],
                                            each['requester_updated_at'],
                                            each['status_updated_at'],
                                            each['initially_assigned_at'],
                                            each['assigned_at'],
                                            each['solved_at'],
                                            each['latest_comment_added_at'],
                                            each['reply_time_in_minutes']['calendar'],
                                            each['reply_time_in_minutes']['business'],
                                            each['first_resolution_time_in_minutes']['calendar'],
                                            each['first_resolution_time_in_minutes']['business'],
                                            each['full_resolution_time_in_minutes']['calendar'],
                                            each['full_resolution_time_in_minutes']['business'],
                                            each['agent_wait_time_in_minutes']['calendar'],
                                            each['agent_wait_time_in_minutes']['business'],
                                            each['requester_wait_time_in_minutes']['calendar'],
                                            each['requester_wait_time_in_minutes']['business'],
                                            each['on_hold_time_in_minutes']['calendar'],
                                            each['on_hold_time_in_minutes']['business'],
                                            each['assignee_stations']])
                        url = old_url['next_page']
                        print(url)
                print("connecting to blob storage")
                blob_service = BlockBlobService(account_name = self.account_name,account_key = self.account_key)
                blob_service.create_blob_from_path('csv-blob', blob_name=typename + '.csv',file_path=self.file_path + typename + '.csv')
                generator = blob_service.list_blobs('csv-blob')
                for blob in generator:
                    print("\t Blob name: " + blob.name)
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)


if __name__ == "__main__":
    #config('john.pham@olinqua.com','Aqualite12@').get_users()
    #config('john.pham@olinqua.com','Aqualite12@').get_ticket_metrics()
    #config('john.pham@olinqua.com','Aqualite12@').get_all_tickets()
    #config('john.pham@olinqua.com','Aqualite12@').get_orgs()
    #config('john.pham@olinqua.com','Aqualite12@').get_groups()







    config('john.pham@olinqua.com','Aqualite12@').get_incremental_ticket(1332034771)
    #config('john.pham@olinqua.com','Aqualite12@').test_post_service()
    #config('john.pham@olinqua.com','Aqualite12@').test_get_service()

