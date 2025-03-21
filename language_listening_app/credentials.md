## How to add Credentials to use google cloud text to speech service ?

For this project i am usinga free tier Google Cloud sandbox account to use necessary services. My credentials keep changing each time i login to the account. We will have to use following steps to be done before consuming a service in the code.

### Enable the Text-to-Speech API

In the Google Cloud Console, navigate to APIs & Services > Library.

Search for "Text-to-Speech API."

Click on it, then click "Enable." If it’s your first time, you may need to set up billing (Google offers a free tier with limits).

### Set Up Authentication

Go to APIs & Services > Credentials.

Click "Create Credentials" and choose "Service Account."

Fill in the details, assign a role (e.g., "Project > Editor"), and click "Done."

### Generate and Download the JSON Key

In the "Service Accounts" list, click on the service account you just created or want to use.

Scroll to the Keys section and click Add Key > Create New Key.

Select JSON as the key type (this is the most common format for client libraries).

Click Create.
You will have an option to download the keys in JSON format

### How to consume in our language listening app ?

Upload the downloaded JSON file to the app when you selec google cloud text to speech option.






