import requests
import sys
import csv
import os
import io
import time
import asyncio

from datetime import date
from azure.storage.blob import BlockBlobService
from io import BytesIO




class config():
    def __init__(self, email, password, delimiter, quote):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session.auth = self.email , self.password
        self.url = 'https://olinqua.zendesk.com/api/v2/'
        self.url_incremental = 'https://olinqua.zendesk.com/api/v2/incremental/'
        self.account_name = ''
        self.account_key = ''
        self.file_path = os.getcwd() + '/'
        self.delimiter = delimiter
        self.quote = quote
        self.quote_normals = csv.QUOTE_NONNUMERIC
        self.blob_bool = True
        self.rmv_file = False
        try:
            self.response = self.session.get(self.url)
            if self.response.status_code != 200:
                print("Not able to login", sys.stderr)
            else:
                print("Login Success",sys.stderr)
        except TimeoutError as err:
            print(err,sys.stderr)

    def blob_upload(self, typename):
        print("connecting to blob storage")
        blob_service = BlockBlobService(account_name = self.account_name,account_key = self.account_key)
        blob_service.create_blob_from_path('csv-blob', blob_name= typename + '.csv',
        file_path=self.file_path + typename + '.csv',timeout=360)
        print("blob uploaded")

    def test_api(self,typename):
        test = self.session.get(self.url + typename + '.json')
        if test.status_code in [200,'200']:
            print("Successful Call")
        else:
            print("Not Successful",sys.stderr)
            print(test.status_code)
            return False
    
    def test_incremental_api(self):
        test = self.session.get(self.url_incremental + '/tickets.json?per_page=1000&start_time=1420070400')
        if test.status_code in [200,'200']:
            print("Successful Call")
        else:
            print("Not Successful",sys.stderr)
            print(test.status_code)
            return False

    def get_all_tickets(self):
        try:
            typename = 'tickets'
            self.test_api(typename)
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
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except UnicodeEncodeError as e:
            print(e,sys.stderr)
    def get_incremental_ticket_events(self):
        try:
            typename = 'incremental_ticket_events'
            self.test_incremental_api()
            with io.open(typename + '.csv','w',newline='',encoding="utf-8") as new_file:
                writer = csv.writer(new_file, delimiter= self.delimiter)
                writer.writerow(['id','ticket_id','timestamp','created_at','updater_id','via','system_lat',
                'system_lng','event_type'])
                old_url = self.url + 'incremental/ticket_events.json?&start_time=1545962247'
                while old_url:
                    old = self.session.get(old_url, stream = True).json()
                    time.sleep(10) ## handle api limits
                    for each in old['ticket_events']:
                        writer.writerow([each['id'],
                                        each['ticket_id'],
                                        each['timestamp'],
                                        each['created_at'],
                                        each['updater_id'],
                                        each['via'],
                                        each['system']['latitude'],
                                        each['system']['longitude'],
                                        each['event_type']])
                    if old_url != old['next_page']:
                        old_url = old['next_page']
                        print(old_url)
                    elif old_url == old['next_page']:
                        old_url = False
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except UnicodeEncodeError as e:
            print(e,sys.stderr)
    def get_incremental_ticket(self):
        try:
            typename = 'incremental_tickets'
            self.test_incremental_api()
            with io.open(typename + '.csv','w',newline='',encoding="utf-8") as new_file:
                writer = csv.writer(new_file, delimiter= self.delimiter)
                writer.writerow(['url','id','external_id','via_channel','created_at','updated_at','type','subject','raw_subject','description',
                'priority','status','recipient','requester_id','submitter_id','assignee_id',
                'organization_id','group_id','collaborator_ids','follower_ids','email_cc_ids','forum_topic_id',
                'problem_id','has_incidents','is_public','due_at','tags','custom_fields','satisfaction_rating','sharing_agreement_ids','fields',
                'followup_ids','brand_id','allow_channelback','allow_attachments','generated_timestamp'])
                old_url = self.url + 'incremental/tickets.json?&start_time=1400070400&updated_at=1310070400'
                while old_url:
                    old = self.session.get(old_url, stream = True).json()
                    for each in old['tickets']:
                        writer.writerow([each['url'],
                                            each['id'],
                                            each['external_id'],
                                            each['via']['channel'],
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
                    if old_url != old['next_page']:
                        old_url = old['next_page']
                        print(old_url)
                    elif old_url == old['next_page']:
                        old_url = False
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except UnicodeEncodeError as e:
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
    def get_groups(self):
        try:
            typename = 'groups'
            self.test_api(typename)
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
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except Exception as e:
            print(e,sys.stderr)
    def get_tags(self):
        try:
            typename = 'tags'
            self.test_api(typename)
            with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                writer.writerow(['name','count','date'])
                url = self.url + typename + '.json'
                while url:
                    old_url = self.session.get(url).json()
                    for each in old_url[typename]:
                        writer.writerow([each['name'],
                                        each['count'],
                                        date.today()])
                    url = old_url['next_page']
                    print(url)
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except Exception as e:
            print(e,sys.stderr)
    def get_activities(self):
        try:
            typename = 'activities'
            self.test_api(typename)
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
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except Exception as e:
            print(e,sys.stderr)
    def get_orgs(self):
        try:
            typename = 'organizations'
            self.test_api(typename)
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
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except Exception as e:
            print(e,sys.stderr)
    def get_metrics_events(self):
        try:
            typename = 'ticket_metric_events'
            self.test_incremental_api()
            with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                writer = csv.writer(new_file, delimiter= self.delimiter,quotechar= self.quote, quoting=self.quote_normals)
                writer.writerow(['id','ticket_id','metric','instance_id','type','time'])
                url = self.url + 'incremental/ticket_metric_events.json?start_time=1583187726'
                while url:
                    old_url = self.session.get(url,stream=True).json()
                    for each in old_url[typename]:
                        writer.writerow([each['id'],
                                        each['ticket_id'],
                                        each['metric'],
                                        each['instance_id'],
                                        each['type'],
                                        each['time']])
                    if url != old_url['next_page']:
                        url = old_url['next_page']
                        print(url)
                    elif url == old_url['next_page']:
                        url = False
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except Exception as e:
            print(e,sys.stderr)
    def get_users(self):
        try:
            typename = 'users'
            self.test_api(typename)
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
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except Exception as e:
            print(e,sys.stderr)
    def get_ticket_metrics(self):
        try:
            typename = 'ticket_metrics'
            self.test_api(typename)
            with io.open(typename + '.csv','w',newline='',encoding='utf-8') as new_file:
                writer = csv.writer(new_file, delimiter= self.delimiter ,quotechar= self.quote, quoting=self.quote_normals)
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
            if self.blob_bool:
                self.blob_upload(typename)
                if self.rmv_file:
                    os.remove(typename + '.csv')
            else:
                print("not uploading")
        except Exception as e:
            print(e,sys.stderr)

if __name__ == "__main__":
    config('john.pham@olinqua.com','Aqualite12@',',','`').get_users()
    config('john.pham@olinqua.com','Aqualite12@',',','`').get_ticket_metrics()
    config('john.pham@olinqua.com','Aqualite12@',',','`').get_all_tickets()
    config('john.pham@olinqua.com','Aqualite12@',',','`').get_orgs()
    config('john.pham@olinqua.com','Aqualite12@',',','`').get_groups()
    config('john.pham@olinqua.com','Aqualite12@',',','`').get_tags()
    #config('john.pham@olinqua.com','Aqualite12@',',','`').get_incremental_ticket()
    config('john.pham@olinqua.com','Aqualite12@',',','`').get_incremental_ticket_events()
    config('john.pham@olinqua.com','Aqualite12@',',','`').get_metrics_events()

