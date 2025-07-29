import time
import base64

import requests
from furl import furl

from .exceptions import LanguageNotFound
from .schemas import CodeSubmission
from .custom_types import Status

class Judge0:
    def __init__(
        self, 
        Judge0_ip: str, 
        X_Auth_Token: str, 
        X_Auth_User: str
    ):
        ''' Init

        Parameters
        ----------
        Judgeo_ip : str
            IP address with port of the Judge0 server
        X_Auth_Token : str
            X-Auth token
        X_Auth_User : str
            X-Auth user
        '''
        self.__judge0_ip = furl(Judge0_ip)
        self.__session: requests.Session = requests.session()
        self.__session.headers['X-Auth-Token'] = X_Auth_Token
        self.__session.headers['X-Auth-User'] = X_Auth_User
        self.__check_tokens()
        self.__init_languages_dict()

    def __check_tokens(
        self
    ):
        ''' Check if the given tokens are valid. If invalid, it raises a requests.HTTPError exception; otherwise, it returns None. 
        '''
        authn_response = self.__session.post(self.__judge0_ip / 'authenticate')
        authn_response.raise_for_status()
        authz_reponse = self.__session.post(self.__judge0_ip / 'authorize')
        authz_reponse.raise_for_status()

    def __init_languages_dict(
        self
    ):
        ''' Initialises all supported languages
        '''
        languages_list = self.__session.get(self.__judge0_ip / 'languages').json()
        self.__languages: dict[int, str] = {item['id']: item['name'] for item in languages_list}

    def __base64_encode(
        self, 
        submission: CodeSubmission
    ) -> CodeSubmission:
        ''' Encodes all string fields in submission with base64
        '''
        new_submission = submission.model_copy()
        new_submission.source_code = base64.b64encode(submission.source_code.encode()).decode()
        if submission.stdin:
            new_submission.stdin = base64.b64encode(submission.stdin.encode()).decode()
        if submission.expected_output:
            new_submission.expected_output = base64.b64encode(submission.expected_output.encode()).decode()
        return new_submission

    @property
    def languages(
        self
    ) -> dict[int, str]:
        '''Returns a dict of available languages

        Returns
        -------
            A dictionary that contatins all supported languages
        '''
        return self.__languages

    def submit(
        self, 
        submission: CodeSubmission, 
        encode_in_base64: bool = True
    ) -> str:
        '''Creates new submission

        Parameters
        ----------
        submission : CodeSubmission
            A submission to create. All str type fields must be plain
        encode_in_base64 : bool
            Whether to encode submission in base64

        Returns
        -------
        str
            A token for the created submission

        Raises
        ------
        LanguageNotFound
        '''
        if self.languages.get(submission.language_id) is None:
            raise LanguageNotFound('Unknown language id. Use languages property to get a dict of available languages')
        
        if encode_in_base64:
            submission = self.__base64_encode(submission)

        data = submission.model_dump(exclude_none=True)

        response = self.__session.post(
            self.__judge0_ip / 'submissions', 
            json=data, 
            params={'base64_encoded': 'true' if encode_in_base64 else 'false'}
        )
        response.raise_for_status()

        token: str = response.json().get('token')
        return token
    
    def submit_batch(
        self, 
        submissions: list[CodeSubmission],
        encode_in_base64: bool = True
    ) -> list[str]:
        '''Creates new submissions

        Parameters
        ----------
        submissions : list[CodeSubmission]
            Submissions to create. All str type fields must be plain
        encode_in_base64 : bool
            Whether to encode submissions in base64

        Returns
        -------
        list[str]
            Tokens for the created submissions

        Raises
        ------
        LanguageNotFound
        '''
        for submission in submissions:
            if self.languages.get(submission.language_id) is None:
                raise LanguageNotFound('Unknown language id. Use languages property to get a dict of available languages')
        
        if encode_in_base64:
            submissions = [self.__base64_encode(submission) for submission in submissions]

        batch_data = [submission.model_dump(exclude_none=True) for submission in submissions]

        response = self.__session.post(
            self.__judge0_ip / 'submissions/batch',
            json={'submissions': batch_data},
            params={'base64_encoded': 'true' if encode_in_base64 else 'false'}
        )
        response.raise_for_status()

        tokens = [item['token'] for item in response.json()]
        return tokens

    def __get_info(
        self, 
        token: str
    ):
        '''Returns reponse body of the GET /submissions/{token} request
        '''
        response = self.__session.get(self.__judge0_ip / 'submissions' / token)
        response.raise_for_status()
        return response.json()
    
    def get_status(
        self, 
        token: str
    ) -> Status:
        '''Returns current status of a sumbmission by its token
        '''
        body: dict = self.__get_info(token)
        return Status(body.get('status').get('id'))
    
    def get_statuses(
        self,
        tokens: list[str]
    ) -> list[Status]:
        ''' Docstring to write
        '''
        return [self.get_status(token) for token in tokens]
    
    def wait_for_completion(
        self, 
        token: str, 
        poll_interval: int = 1
    ) -> Status:
        ''' Waits for a submission to complete and returns its final status
        '''
        while 1:
            status = self.get_status(token)
            if status in [Status.IN_QUEUE, Status.PROCESSING]:
                time.sleep(poll_interval)
                continue
            return status
        
    def wait_for_completions(
        self,
        tokens: list[str],
        poll_interval: int = 1
    ) -> list[Status]:
        ''' Docstring to write
        '''
        statuses = []
        for token in tokens:
            statuses.append(self.wait_for_completion(token, poll_interval))
        return statuses
