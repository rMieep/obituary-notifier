<div id="top"></div>
<!-- ABOUT THE PROJECT -->

## Obituary Notifier

Obituary Notifier is a small framework that can be used to fetch obitauries from undertaker websites and notify external users about obituaries matching predefined keywords. The framework exposes four extensions points:

* Undertaker
* Notifier
* EMailClient
* ObituaryRepository

### Extension Points
#### Undertaker
This interface can be extended to provide an implementation for a specific undertaker. The interface exposes two methods:

* get_obituaries(): Fetches a list of obituaries from the undertaker
* get_description(obituary): Fetches the description of an obituary from that undertaker

#### Notifier
This interface can be extended to notify external users about matching obituaries. Currently the framework provides the EMailNotifier implementation which notifies external users via email. The interface exposes one method:

* notify(obituary): Notifies the external user about the obituary

#### EMailClient
This interface can be extended to provide a custom EMailClient. Currently the framework provides two implementations. The GMailClient and the SMTPEMailClient. The GMailClient uses the GMail API for authentication and sending emails while the SMTPEMailClient uses SMTP and TLS. The Interface exposes a context manager, a public and a private mthode:

* context manager: Authenticates the user
* send(subject, message): sends the email
* _build_email(receiver_address, subject, message): builds the email object

#### ObituaryRepository
This interface can be extended to provide a custom database implementation. A default implementation using a local SQLite database is provided. The interface exposes three methods:

* add(obituary): Adds obituary to db
* exists(obituary): Checks if the obituary already exists in the db
* clean_up(): Removes old obituaries

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started
1. Clone the repo
   ```sh
   git clone https://github.com/rMieep/obituary-notifier.git
   ```
2. Install pip packages
   ```sh
   pip install -r requirements.txt
   ```
3. Inject your dependencies in `main.py`
   * create_keywords()
   * create_undertaker()
   * create_notifier()
   * create_obituary_repository()

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

The project currently runs on a rasberry pi and is executed every morning. The project is used to notify people from my village about current funerals so that they can either attend them or write their condolences. Otherwise they would have to check the websites of the local undertakers frequently. The program is executed using a cron job as well as a bash script to activate the virtual enviroment and load the dependencies.

The bash script:
```sh
   #!/bin/bash
   source /home/pi/obituary-notifier/venv/bin/activate
   pip install -r requirements.txt
   python3 main.py
   ```
The cron job:
```sh
   0 7 * * * /bin/bash /home/pi/obituary-notifier/runner.sh
   ```

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>
