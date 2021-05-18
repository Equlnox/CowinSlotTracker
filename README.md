# CowinSlotTracker
## Requirements -
Add a secrets.env with format - 
Follow this guide to setup your gmail account to send emails programatically - 
https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development
```
GMAIL_ADDRESS=<Your-email>
GMAIL_APP_PASSWORD=<Your-email-password>
```
If you turn less secure apps off, you can directly use your GMAIL password in `GMAIL_APP_PASSWORD`.
Otherwise create an app password and use that (https://myaccount.google.com/apppasswords)

## Usage -
`docker build -t vaccine-notifier .`
`docker run --env-file secrets.env vaccine-notifier "Madhya Pradesh" Indore --email-address myemail@domain.com`

## More info -
`docker run vaccine-notifier -h`
