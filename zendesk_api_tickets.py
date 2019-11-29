import requests
import sys
import csv


class config():
    def __init__(self, email, password):
        self.email = email
        self.password = password
        authentication = self.email , self.password
        self.session = requests.Session()
        self.session.auth = authentication
        self.url = 'https://olinqua.zendesk.com'
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
            test = self.session.get(self.url + '/api/v2/tickets.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with open('tickets.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= ',')
                    writer.writerow(['status','type','external_id','via','recipient','requester_id','submitter_id',
                    'assignee_id','organization_id','has_incidents','url','id','created_at','subject',
                    'priority','custom_fields'])
                    url = self.url + '/api/v2/tickets.json'
                    while url:
                        data = self.session.get(url).json()
                        for each in data['tickets']:
                            writer.writerow([each['status'],
                                            each['type'],
                                            each['external_id'],
                                            each['via'],
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
                                            each['custom_fields']])
                        url = data['next_page']
                        print(url)
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)

    def get_incremental_ticket(self,unix_time):
        try:
            data = self.session.get(self.url + '/api/v2/incremental/tickets.json?start_time={}'.format(str(unix_time)))
            if data.status_code in [200,'200']:
                print("Successful Call")
                print(data.content)
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)

    def test(self):
        try:
            data = self.session.get(self.url + '/api/v2/satisfaction_ratings.json')
            if data.status_code in [200,'200']:
                print("Successful Call")
                print(data.content)
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)

    
    def get_users(self):
        try:
            test = self.session.get(self.url + '/api/v2/users.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with open('users.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= ',')
                    writer.writerow(['id','url','name','email','created_at','updated_at','time_zone'])
                    url = self.url + '/api/v2/users.json'
                    while url:
                        old_url = self.session.get(url).json()
                        for each in old_url['users']:
                            writer.writerow([each['id'],
                                            each['url'],
                                            each['name'],
                                            each['email'],
                                            each['created_at'],
                                            each['updated_at'],
                                            each['time_zone']])
                        url = old_url['next_page']
                        print(url)  
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)


    def get_ticket_metrics(self):
        try:
            test = self.session.get(self.url + '/api/v2/ticket_metrics.json')
            if test.status_code in [200,'200']:
                print("Successful Call")
                with open('ticket_metrics.csv','w',newline='',encoding='utf-8') as new_file:
                    writer = csv.writer(new_file, delimiter= ',')
                    writer.writerow(['url','id','ticket_id','created_at','updated_at','group_stations','reopens',
                    'replies','assignee_updated_at','requester_updated_at','status_updated_at','initially_assigned_at',
                    'status_updated_at','status_updated_at','initially_assigned_at','assigned_at','solved_at',
                    'latest_comment_added_at','reply_time_in_minutes','first_resolution_time_in_minutes','full_resolution_time_in_minutes',
                    'agent_wait_time_in_minutes','requester_wait_time_in_minutes','on_hold_time_in_minutes','assignee_stations'])
                    url = self.url + '/api/v2/ticket_metrics.json'
                    while url:
                        old_url = self.session.get(url).json()
                        for each in old_url['ticket_metrics']:
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
                                            each['reply_time_in_minutes'],
                                            each['first_resolution_time_in_minutes'],
                                            each['full_resolution_time_in_minutes'],
                                            each['agent_wait_time_in_minutes'],
                                            each['requester_wait_time_in_minutes'],
                                            each['on_hold_time_in_minutes'],
                                            each['assignee_stations']])
                        url = old_url['next_page']
                        print(url)  
            else:
                print("Not Successful",sys.stderr)
                return False
        except Exception as e:
            print(e,sys.stderr)
    def get_satisfactions(self):
        pass




if __name__ == "__main__":
    #config('','').get_users()
    #config('','').get_ticket_metrics()
    #config('','').get_all_tickets()
    config('','').test()











