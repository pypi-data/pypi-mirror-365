# easybrevo

Use [Brevo API](https://developers.brevo.com/reference/) with Python (the easy way).

## Installation

```bash
pip install easybrevo
```

## Usage

First of all, you have to instantiate an API client:

```python
from easybrevo import ApiClient

client = ApiClient()
```

`ApiClient()` admits one argument `api_key` → Brevo API key (Generate from [here](https://developers.brevo.com/docs/getting-started#using-your-api-key-to-authenticate)).

If `api_key` is not provided, its value will be collected from a `.env` file or an environment variable. Otherwise an error will raise.

### Sending an email

The quickest way to send an email is the following:

```python
client.send_email(
    to="hello@example.com",
    subject="This is the subject",
    content="This is the content"
)
```

#### Sender

`send_mail()` admits arguments `sender_email` and `sender_name` in order to set sender information when sending the email.

If these arguments are not provided, its value will be collected from a `.env` file or an environment variable.

#### Content type

By default, the content of the email is intepreted as _plain text_, but this behaviour can be changed with the argument `content_type`:

- `content_type='txt'` → Text (default)
- `content_type='md'` → Markdown
- `content_type='html'` → HTML

#### Attachments

You can attach files to the email using `attachments` argument.

It can contain a single file (path) or a list of file paths to be included as attachments in the email.
