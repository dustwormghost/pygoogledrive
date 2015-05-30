''' Google Drive API '''
import utils

from apiclient.http import MediaFileUpload, HttpRequest 
from apiclient import errors 

class DriveApi:
    def upload_file(self, service, file_name, mime_type, body):
        '''upload one file with type and description
        Args:
            service: Drive service instance
            file: file path with file name
            mime_type: is it text or binary stream, i.e., application/octet-stream
            body: metadata, i.e. {'title': 'jar_file.jar', 'description': 'My jar file', 'mimeType': 'application/octet-stream'}
        Returns:
            file upload details, path to file, permissions, etc.
        '''
        try:
            media_body = MediaFileUpload(file_name, mimetype=mime_type, resumable=True)
            return service.files().insert(body=body, media_body=media_body).execute()
        except errors.HttpError, error:
            if error.resp.status in [404]:
                utils.log('Page not found:' + error)
            elif error.resp.status in [500, 502, 503, 504]:
                utils.log('Service unavailable. Try again later:' + error)
            else:
                utils.log('Failed to upload files - Unknown error:' + error)
    
    def upload_and_delete_files_wrapper(self, service, from_dir_path, files_upload, files_delete):
        '''
        Args:
            service: drive api service instance
            from_dir_path: directory path to upload files from
            files_upload: list of files to upload
            files_to_delete: list of files under from_dir_path, used to purge directory after upload completes
        '''
        utils.log('Upload ' + str(len(files_upload)) + ' file(s)')
        for f in files_upload:
            self.upload_file(service, ''.join([from_dir_path, f]), 'application/octet-stream', body={'title': f, 'description': 'zip file', 'mimeType': 'application/octet-stream'})
            files_delete.append(f)
            print '*',
        utils.log('Uploaded')
        utils.delete_files(from_dir_path, files_delete)
            