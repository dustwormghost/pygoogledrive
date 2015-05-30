import utils
import time

from oauth import OAuthDriveAPI, OAuthGmailAPI
from driveapi.driveapi import DriveApi
from gmailapi.gmailapi import GmailAPI
from datetime import datetime



# threads = gmailApi.get_page_of_threads(service, 'me');

# if threads['threads']:
#     for thread in threads['threads']:
#         print thread

# messagesIds = gmailApi.get_messages_ids_with_matching_query(service, 'me', 'from:mmalinowski@42six.com')
# labels = gmailApi.get_all_labels(service, 'me')



# from subprocess import call
# cams = ['FRONT', 'BACK']
# cams_lst = {cams[0]: 'front.lst', cams[1]: 'back.lst'}
#
# ffmpeg_cmd = ["./ffmpeg/ffmpeg", "-r", "1/10", "-f", "concat", "-i", "6", "-c", "copy", "9"]
# call(ffmpeg_cmd)



def gmail():
    # Gmail API
    gmail_service = OAuthGmailAPI('secret/client_secret.json', 'FULL').get_gmail_service()
    gmailApi = GmailAPI()

    msgIds = gmailApi.get_attachments_and_save_wrapper(gmail_service, user_id='me', label='INBOX', out_dir=path)
    if len(msgIds) is 0:
        utils.log('No messages found. Sleep and continue.')
        time.sleep(60)

    gmailApi.delete_msgs_wrapper(gmail_service, msgIds, 'me')


def run_security():
    '''
    Get files from given path
    Zip files from given path
    Upload zip file to google drive
    Delete files from given path
    '''
    path = '/Users/ftp-user/Public/'

    drive_service = OAuthDriveAPI('secret/drive_client_secret.json', 'FULL', False).get_drive_service()
    driveApi = DriveApi()

    sleep_time = 60 #seconds
    sleep_time_next_upload = 60 #seconds

    while(True):
        # find all attachments, save to hdd, delete messages

        # list files for upload
        files = utils.list_files(path)

        if len(files) is 0:
            utils.log('No files to upload. Sleep and continue.')
            time.sleep(sleep_time)

        # zip files
        time_format = '%b-%d-%Y-%H-%M-%S'
        zip_file_name = datetime.today().strftime(time_format) + '.zip'
        zip_o_path = ''.join([path, zip_file_name])
        if not utils.create_zip_file(path, zip_o_path, files):
            print 'Failed to create zip file. Sleep and try again.'
            time.sleep(sleep_time)
            continue

        # upload files, delete files from local drive
        driveApi.upload_and_delete_files_wrapper(drive_service, path, [zip_file_name], files)

        time.sleep(sleep_time_next_upload)
    

run_security()