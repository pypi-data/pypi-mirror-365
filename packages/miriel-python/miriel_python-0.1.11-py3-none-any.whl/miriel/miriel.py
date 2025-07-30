import requests, os, time
from urllib.parse import urlparse
import json

COMMON_FILE_EXTENSIONS = [
    # Documents
    '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.tex', '.md', '.markdown',
    
    # Spreadsheets / Data
    '.csv', '.tsv', '.xls', '.xlsx', '.ods', '.json', '.xml', '.yaml', '.yml', '.parquet',
    
    # Presentations
    '.ppt', '.pptx', '.odp',

    # Code / Config
    '.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.rb', '.go', '.sh', '.html', '.css',
    '.ipynb', '.ini', '.cfg', '.env', '.toml', '.bat',

    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.webp', '.ico',

    # Archives / Compressed
    '.zip', '.tar', '.gz', '.rar', '.7z', '.xz',

    # Audio / Video
    '.mp3', '.wav', '.aac', '.flac', '.ogg',
    '.mp4', '.mov', '.avi', '.mkv', '.webm',

    # Misc
    '.log', '.db', '.sqlite', '.bin', '.exe'
]

def looks_like_path(s):
    s = s.strip()
    return (
        s.startswith(("~", ".", "..", os.sep)) or
        os.name == "nt" and re.match(r"^[a-zA-Z]:[\\/]", s) or
        os.path.sep in s or
        any(s.lower().endswith(ext) for ext in COMMON_FILE_EXTENSIONS)
    )

def is_uri(s):
    """Return True if s is an HTTP/S (or other supported) URI."""
    p = urlparse(s)
    return (
        p.scheme in (
                'http', 'https', 'file', 'folder', 'directory', 'dir',
                's3', 'rtsp', 'discord', 'gcalendar', 'string'
            )
        and (p.netloc or p.path)
    )

class Miriel:
    def __init__(self, api_key=None, base_url="https://api.prod.miriel.ai", verify=True):
        if not api_key:
            raise ValueError(
                "API key is required. Please visit https://miriel.ai to sign up."
            )
        self.api_key = api_key
        self.base_url = base_url
        self.verify = verify

    def serialize_payload_for_form(self, payload):
        """Convert all nested dicts/lists in the payload to JSON strings."""
        serialized = {}
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                serialized[key] = json.dumps(value)
            else:
                serialized[key] = value
        return serialized

    def make_post_request(self, url, payload=None, files=None):
        """
        Makes a POST request to the given URL.

        - If 'files' is provided, sends a multipart/form-data request:
        - The 'payload' is included as regular form fields via the 'data=' parameter.
        - Otherwise, sends a JSON body using the 'json=' parameter.
        """
        if files:
            # For file uploads (multipart/form-data)
            # 'payload' is sent as form fields in data=
            headers = {
                'x-access-token': self.api_key,
                'Accept': 'application/json'
                # Don't set 'Content-Type' here, requests does it automatically 
                # when using files= parameter
            }
            payload = self.serialize_payload_for_form(payload)
            response = requests.post(
                url,
                headers=headers,
                files=files, 
                data=payload,  # form fields
                verify=self.verify
            )
        else:
            # For JSON-based requests
            headers = {
                'Content-Type': 'application/json',
                'x-access-token': self.api_key,
            }
            response = requests.post(
                url,
                headers=headers,
                json=payload,  # JSON body
                verify=self.verify
            )

        # Common response handling
        if response.status_code == 401:
            raise ValueError("Invalid API key. Please visit https://miriel.ai to sign up.")
        if response.status_code in [200, 201]:
            try:
                return response.json()
            except ValueError:
                print(f"Error parsing JSON response: {response.text}")
                return None
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    
    def query(self, query, **params):
        """required: query
        optional: input_images, response_format, user_id, project, metadata_query, num_results, want_llm, want_vector, want_graph, mock_response"""
        url = f"{self.base_url}/api/v2/query"
        payload = {"query": query, **{k: v for k, v in params.items() if v is not None}}
        return self.make_post_request(url, payload=payload)

    def learn(self, input, user_id=None, metadata=None, force_string=False, discoverable=True, grant_ids=["*"], domain_restrictions=None, recursion_depth=0, priority=100, project=None, wait_for_complete=False, chunk_size=None, polling_interval=None):
        """Add a string, URL, or file to the Miriel AI system for learning.
        If input is a valid path to a file or directory, uploads its contents.
        If the input looks like a path but doesn't exist, raises FileNotFoundError.
        Otherwise, input is treated as a literal string.  Force_string=True will 
        treat it as a string always."""
        # Handle file/directory path resolution
        if isinstance(input, str):
            expanded_path = os.path.expanduser(input)
            resolved_path = os.path.abspath(expanded_path)

            if os.path.exists(resolved_path):
                if not looks_like_path(input):
                    print(f"[Info] Input '{input}' did not look like a path, but a file was found and will be uploaded.")
                input = resolved_path
                is_file = True
                is_directory = os.path.isdir(resolved_path)
            elif is_uri(input) and not force_string:
                is_file = False
                is_directory = False
            elif looks_like_path(input) and not force_string:
                raise FileNotFoundError(
                    f"Input '{input}' looks like a file or path, but no file was found at: {resolved_path}.\n"
                    "Hint: If this was meant to be a text string, use force_string=True."
                )
            else:
                is_file = False
                is_directory = False
        else:
            if not force_string:
                raise TypeError(
                    f"Unsupported input type: {type(input)}. Provide a string path or literal string. "
                    "Use force_string=True to override."
                )
            is_file = False
            is_directory = False
        
        #convert string priorities to integers
        if isinstance(priority, str):
            if priority == "norank":
                priority = -1
            elif priority == "pin":
                priority = -2
        payload = {
            "user_id": user_id,
            "metadata": metadata,
            "force_string": force_string,
            "discoverable": discoverable,
            "grant_ids": grant_ids,
            "domain_restrictions": domain_restrictions,
            "recursion_depth": recursion_depth,
            "priority": priority,
            "chunk_size": chunk_size,
            "polling_interval": polling_interval
        }
        if project is not None:
            payload["project"] = project
        if is_file:
            endpoint = f"{self.base_url}/api/v2/learn"
            files_list = []
            
            if is_directory:
                # Walk through directory and add all files
                for dirpath, _, filenames in os.walk(input):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        files_list.append(
                            (
                                "files",  # send every file under the same field name
                                (
                                    filename,
                                    open(filepath, "rb"),
                                    "application/octet-stream"
                                )
                            )
                        )
            else:
                # Single file
                filename = os.path.basename(input)
                files_list.append(
                    (
                        "files",
                        (
                            filename,
                            open(input, "rb"),
                            "application/octet-stream"
                        )
                    )
                )

            print(f"Uploading {len(files_list)} files…", payload)
            response = self.make_post_request(url=endpoint, payload=payload, files=files_list)
        else:
            endpoint = f"{self.base_url}/api/v2/learn"
            payload["input"] = input
            response = self.make_post_request(url=endpoint, payload=payload)
        
        if wait_for_complete:
            while self.count_non_completed_learning_jobs() > 0:
                print("Waiting for all learning jobs to complete...")
                time.sleep(1)
        return response
    
    def get_learning_jobs(self):
        get_job_status_url = f'{self.base_url}/api/v2/get_monitor_jobs'
        get_job_status_response = self.make_post_request(get_job_status_url, payload = {"job_status": "all"})
        return get_job_status_response
    
    def count_non_completed_learning_jobs(self):
        jobs = self.get_learning_jobs()
        if not jobs:
            return 0
        pending_count = sum(len(group.get('job_list', [])) for group in jobs.get('pending_jobs', []))
        queued_count = len(jobs.get('queued_items', []))
        return pending_count + queued_count
    
    def update_document(self, document_id, user_id = None, metadata=None, discoverable=True, grant_ids=["*"], chunk_size=None):
        update_document_url = f'{self.base_url}/api/v2/update_document'
        update_document_response = self.make_post_request(update_document_url, payload = { "user_id": user_id, "document_id": document_id, "metadata": metadata, "discoverable": discoverable, "grant_ids": grant_ids, "chunk_size": chunk_size})
        return update_document_response
    
    def create_user(self):
        create_user_url = f'{self.base_url}/api/v2/create_user'
        create_user_response = self.make_post_request(create_user_url, payload = {})
        return create_user_response

    def set_document_access(self, user_id, document_id, grant_ids):
        set_document_access_url = f'{self.base_url}/api/v2/set_document_access'
        set_document_access_response = self.make_post_request(set_document_access_url, payload = { "user_id": user_id, "document_id": document_id, "grant_ids": grant_ids})
        return set_document_access_response

    def get_document_by_id(self, document_id, user_id = None):
        get_document_by_id_url = f'{self.base_url}/api/v2/get_document_by_id'
        get_document_by_id_response = self.make_post_request(get_document_by_id_url, payload = { "user_id": user_id, "document_id": document_id})
        return get_document_by_id_response

    def get_monitor_sources(self, user_id = None):
        get_monitor_sources_url = f'{self.base_url}/api/v2/get_monitor_sources'
        get_monitor_sources_response = self.make_post_request(get_monitor_sources_url, payload = { "user_id": user_id})
        return get_monitor_sources_response

    def remove_all_documents(self, user_id = None):
        remove_all_documents_url = f'{self.base_url}/api/v2/remove_all_documents'
        remove_all_documents_response = self.make_post_request(remove_all_documents_url, payload = { "user_id": user_id})
        return remove_all_documents_response

    def get_users(self):
        get_users_url = f'{self.base_url}/api/v2/get_users'
        get_users_response = self.make_post_request(get_users_url, payload = {})
        return get_users_response

    def delete_user(self, user_id):
        delete_user_url = f'{self.base_url}/api/v2/delete_user'
        delete_user_response = self.make_post_request(delete_user_url, payload = { "user_id": user_id})
        return delete_user_response

    def get_projects(self):
        """Get all projects belonging to the authenticated user"""
        get_projects_url = f'{self.base_url}/api/v2/get_projects'
        response = self.make_post_request(get_projects_url, payload={})
        return response

    def create_project(self, name):
        """Create a new project with the specified name"""
        create_project_url = f'{self.base_url}/api/v2/create_project'
        response = self.make_post_request(create_project_url, payload={"name": name})
        return response

    def delete_project(self, project_id):
        """Delete a project with the specified ID"""
        delete_project_url = f'{self.base_url}/api/v2/delete_project'
        response = self.make_post_request(delete_project_url, payload={"project_id": project_id})
        return response

    def get_document_count(self):
        """Get the count of documents for the authenticated user"""
        get_document_count_url = f'{self.base_url}/api/v2/get_document_count'
        response = self.make_post_request(get_document_count_url, payload={})
        return response

    def get_user_policies(self):
        """Get all policies for the authenticated user"""
        get_user_policies_url = f'{self.base_url}/api/v2/get_user_policies'
        response = self.make_post_request(get_user_policies_url, payload={})
        return response

    def add_user_policy(self, policy, project_id=None):
        """Add a policy for the authenticated user, optionally associated with a project"""
        add_user_policy_url = f'{self.base_url}/api/v2/add_user_policy'
        payload = {"policy": policy}
        if project_id is not None:
            payload["project_id"] = project_id
        response = self.make_post_request(add_user_policy_url, payload=payload)
        return response

    def delete_user_policy(self, policy_id, project_id=None):
        """Delete a policy for the authenticated user by its ID, optionally associated with a project"""
        delete_user_policy_url = f'{self.base_url}/api/v2/delete_user_policy'
        payload = {"policy_id": policy_id}
        if project_id is not None:
            payload["project_id"] = project_id
        response = self.make_post_request(delete_user_policy_url, payload=payload)
        return response

    def remove_document(self, document_id, user_id=None):
        """Remove a specific document by its ID"""
        remove_document_url = f'{self.base_url}/api/v2/remove_document'
        response = self.make_post_request(remove_document_url, payload={"document_id": document_id, "user_id": user_id})
        return response

    def get_all_documents(self, user_id=None, project=None, metadata_query=None):
        """Get all documents, optionally filtered by project, user_id, or metadata query"""
        get_all_documents_url = f'{self.base_url}/api/v2/get_all_documents'
        payload = {}
        if user_id is not None:
            payload["user_id"] = user_id
        if project is not None:
            payload["project"] = project
        if metadata_query is not None:
            payload["metadata_query"] = metadata_query
            
        response = self.make_post_request(get_all_documents_url, payload=payload)
        return response

    def remove_resource(self, resource_id, user_id=None):
        """Remove a specific resource by its ID"""
        remove_resource_url = f'{self.base_url}/api/v2/remove_resource'
        payload = {"resource_id": resource_id}
        if user_id is not None:
            payload["user_id"] = user_id
        response = self.make_post_request(remove_resource_url, payload=payload)
        return response
