from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

def init():
    # Below code does the authentication
    # part of the code
    gauth = GoogleAuth()

    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    drive_client = GoogleDrive(gauth)
    return drive_client


# replace the value of this variable
# with the absolute path of the directory
path = "/Users/asafsmac/code/stock-info"

drive_folder_id = "1ygZq8BJ-zsqGsbKxFFLb6jXFu5BnkPT8"




def upload_to_drive(drive_client, file_path: str):
    _fn = file_path.split("/")[-1]
    #
    print(f'uploading {_fn}..')
    f = drive_client.CreateFile({'title': _fn, 'parents': [{'id': drive_folder_id}]})
    f.SetContentFile(file_path)
    f.Upload()
    print(f'uploaded {_fn} Successfully !')
    # Due to a known bug in pydrive if we
    # don't empty the variable used to
    # upload the files to Google Drive the
    # file stays open in memory and causes a
    # memory leak, therefore preventing its
    # deletion
    f = None


# README :
# used for authenticating and generating code https://pythonhosted.org/PyDrive/quickstart.html#authentication
# https://www.youtube.com/watch?v=bkZns_VOB6I&ab_channel=mb-techs - add permission for specific user
# https://pythonhosted.org/PyDrive/quickstart.html#authentication - save credentials
