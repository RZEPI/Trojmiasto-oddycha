# Trójmiasto oddycha

The goal is to help LPP keep their workplace safe and healthy by continuously monitoring air quality and environmental conditions. This application integrates with the Airthings API to collect real-time data from workplace sensors. The collected data is then analyzed and reported to relevant stakeholders via email.

## Prerequisites

Make sure you have Python version 3.10 or higher installed. Python 3.10 is the version we've tested, but the program may work with other versions as well. You can verify your Python version by running the following command:

```bash
python --version
```

## Setting Up the Project

Install Python: Download and install Python 3.10 from the official Python website: https://www.python.org/downloads/

#### Clone the repository to your local machine:

```bash
git clone https://github.com/RZEPI/Trojmiasto-oddycha.git TrojmiastoOddycha
cd TrojmiastoOddycha
```

#### Create a Virtual Environment (optional, but recommended):

```bash
python -m venv venv
```

#### Activate the Virtual Environment:

- On Windows, activate the virtual environment by running:
    ```bash
    .\venv\Scripts\activate
    ```
- On macOS/Linux, use the following command:
    ```bash
    source venv/bin/activate
    ```

#### Install Dependencies:
    
    pip install -r requirements.txt

## Fill out .env.example file
- **CLIENT_ID, CLIENT_SECRET:** You can aquire these by going to Integrations > API and selecting *WSB* client on airthing website.
- **LOCATION_ID:** LPP SILK location id which you can get from [ext-api.airthings.com/v1/locations](https://ext-api.airthings.com/v1/locations) by a GET request.
You can acquire Authorization token by logging in [accounts.airthings.com/authorize](https://accounts.airthings.com/authorize). 
For your convinience airhings provides [API reference](https://developer-business.airthings.com/reference/getv1locations).
- **SENDER:** From what email address the reports will be sent.
- **RECIPIENT:** Recipent of the reports. Can provide multiple seperating them by a comma.
- **SMTP_SERVER:** Address of smtp server.
- **SMTP_PORT:** Port of the server.
- **SMTP_PASSWORD:** A password to authenticate to SMTP server.

After you filled the required fields remove ".example" from the file name.

## Running the Application

You can start the script by running:

```bash
python sampleCollector.py
```

This will start the main loop, which will collect data from airthings and delegate tasks to other scripts:

To learn more about AirthingsAPI visit official [documentation](https://developer.airthings.com/docs/api-getting-started/index.html).

## Contributing:

After you've cloned the repository and activated your virtual environment please stick to the following flow:

Create a new branch for your changes:

```bash
git checkout -b feature-name
```

Make your changes, then stage and commit them:

```bash
git add .
git commit -m "Description of changes"
```

Push your branch to the remote repository:

```bash
git push origin feature-name
```

Create a Pull Request: 
Go to the GitHub repository, create a pull request from your branch, and after approval merge using **squash and merge option**.
