import os.path

from watchdog.events import FileSystemEventHandler
import requests
from src.DBHandler import DBHandler


class KnowledgeSync(FileSystemEventHandler):
    db_name = '/config/files.db'
    def __init__(self, config):
        self.knowledge_id = config['knowledge_id']
        self.webuiurl = config['url']
        self.token = config['token']
        self.allowed_ext = config['synced_extensions']
        initial_sync_necessary = not os.path.isfile(self.db_name)
        self.db = DBHandler(self.db_name)
        if initial_sync_necessary:
            self.initial_sync(config['watch_directory'])

    def __upload_file(self, file_path):
        url = f'{self.webuiurl}/api/v1/files/'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json'
        }
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, headers=headers, files=files)
        return response.json()

    def __add_file_to_knowledge(self, file_id):
        url = f'{self.webuiurl}/api/v1/knowledge/{self.knowledge_id}/file/add'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {'file_id': file_id}
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def add_file(self, path):
        file_info = self.__upload_file(path)
        self.db.add_file(path, file_info['id'])
        self.__add_file_to_knowledge(file_info['id'])

    def on_created(self, event):
        if event.src_path.split('.')[-1] not in self.allowed_ext:
            return
        #print(f'New file detected: {event.src_path}')
        self.add_file(event.src_path)

    def __remove_file_from_knowledge(self, file_id):
        url = f'{self.webuiurl}/api/v1/knowledge/{self.knowledge_id}/file/remove'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {'file_id': file_id}
        response = requests.post(url, headers=headers, json=data)
        #print(response, response.json())
        return response.json()

    def __remove_file(self, file_id):
        url = f'{self.webuiurl}/api/v1//files/${file_id}'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {'file_id': file_id}
        response = requests.delete(url, headers=headers, json=data)
        #print(response, response.json())
        return response.json()

    def delete_file(self, path):
        id = self.db.retrieve_file(path)[0][1]
        self.__remove_file_from_knowledge(id)
        self.db.delete_file(path)

    def on_deleted(self, event):
        if event.src_path.split('.')[-1] not in self.allowed_ext:
            return
        #print(f'File deleted: {event.src_path}')
        self.delete_file(event.src_path)

    def update_file(self, file_path, file_id):
        url = f'{self.webuiurl}/api/v1/files/${file_id}/data/content/update'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json'
        }
        files = {'content': open(file_path, 'rb')}
        response = requests.post(url, headers=headers, files=files)
        #print(response, response.json())
        return response.json()

    def update_to_knowledge(self, file_id):
        url = f'{self.webuiurl}/api/v1/knowledge/{self.knowledge_id}/file/update'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {'file_id': file_id}
        response = requests.post(url, headers=headers, json=data)
        #print(response, response.json())
        return response.json()

    # updated file
    def on_modified(self, event):
        if event.src_path.split('.')[-1] not in self.allowed_ext:
            return
        if os.path.isdir(event.src_path):
            return
        #print(f'File modified: {event.src_path}')
        self.delete_file(event.src_path)
        self.add_file(event.src_path)
        return
        #id = self.db.retrieve_file(event.src_path)[0][1]
        #self.update_file(event.src_path, id)
        #self.update_to_knowledge(id)

    def __reset_knowledge(self):
        url = f'{self.webuiurl}/api/v1/knowledge/{self.knowledge_id}/reset'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers)
        #print(response, response.json())
        return response.json()

    def initial_sync(self, path):
        print('Starting initial sync!')
        self.__reset_knowledge()
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                if name.split('.')[-1]  in self.allowed_ext:
                    self.add_file(os.path.join(root, name))
        print('Initial sync successful!')