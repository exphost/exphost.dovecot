import pytest
import random
import time

def run_commands(cmds, host):
    cmd = "echo -e '" + r"\r\n".join(cmds) + r"\r\na logout' | openssl s_client -connect 127.0.01:993 -ign_eof"
    return host.check_output(cmd)

def place_email(host):
    email = {
        'from': 'test@domena5.ru',
        'to': 'mariola@domena6.ru',
        'subject': 'auto_test_{}'.format(random.random()),
        'data': 'hello test'
    }
    host.ansible(
      "copy",
      "dest=/var/lib/vmail/domena6.ru/mariola/new/{subject} content='From: {from}\nTo: {to}\nSubject: {subject}\n\n{data}'".format(**email),
      become=True,
      become_user="root",
      check=False,
    )
    return email

def clear_email(host, email):
    host.ansible(
      "shell",
      'grep -l -r  "Subject: {subject}" /var/lib/vmail/|xargs -r rm'.format(subject=email['subject']),
      become=True,
      become_user="root",
      check=False,
    )

def test_dovecot_running(host):
    assert host.service("dovecot").is_running

def test_dovecot_user_login(host):
    assert "a1 OK" in run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        ],
        host)

def test_dovecot_user_login_bad_credentials(host):
    assert "a1 OK" not in host.check_output("""echo -e "a1 login mariola@domena6.ru mariolapass2\r\na logout" | openssl s_client -connect 127.00.1:993 -ign_eof""")
    assert "a1 OK" not in run_commands(
        [
            "a1 login mariola@domena6.ru mariolapass2",
        ],
        host)

def test_dovecot_list_folders(host):
    output = run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        'a2 list "" "*"',
        ],
        host)
    assert "a2 OK List completed" in output
    assert "INBOX" in output

def test_dovecot_create_folder(host):
    assert "a2 OK Create complete" in run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        "a2 create test1",
        ],
        host)
    assert "test1" in run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        'a2 list "" "*"',
        ],
        host)
    assert "a2 OK Delete complete" in run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        "a2 delete test1",
        ],
        host)
    assert "test1" not in run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        'a2 list "" "*"',
        ],
        host)

def test_dovecot_list_emails(host):
    # Check if number of listed email increased
    # before: * SEARCH 1 2
    # after: * SEARCH 1 2 3 4
    search_before = None
    search_after = None

    output = run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        'a2 SELECT INBOX',
        'a3 search new',
        ],
        host).split("\n")
    for line in output:
        if line.startswith("* SEARCH"):
            search_before = line
    email1 = place_email(host)
    email2 = place_email(host)
    time.sleep(3)

    output = run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        'a2 SELECT INBOX',
        'a3 search all',
        ],
        host).split("\n")
    for line in output:
        if line.startswith("* SEARCH"):
            search_after = line

    clear_email(host, email1)
    clear_email(host, email2)
    search_before_count = len(search_before.split(' '))
    search_after_count = len(search_after.split(' '))
    assert search_before_count + 2 == search_after_count

def test_dovecot_read_email(host):
    email = place_email(host)
    time.sleep(3)

    imap_message_id = -1
    output = run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        'a2 SELECT INBOX',
        'a3 search all',
        ],
        host).split("\n")
    for line in output:
        if line.startswith("* SEARCH"):
            imap_message_id = int(line.split(' ')[-1]) # the newest email

    output = run_commands(
        [
        "a1 login mariola@domena6.ru mariolapass",
        'a2 SELECT INBOX',
        'a3 fetch {id} body[]'.format(id=imap_message_id),
        ],
        host)
    clear_email(host, email)
    assert "From: {email_from}".format(email_from = email['from']) in output
    assert "To: {to}".format(to = email['to']) in output
    assert "Subject: {subject}".format(subject = email['subject']) in output
