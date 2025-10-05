-- Users table
CREATE TABLE users (
    user_id NUMBER PRIMARY KEY,
    username VARCHAR2(100) NOT NULL UNIQUE,
    email VARCHAR2(255) NOT NULL UNIQUE,
    password_hash VARCHAR2(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_users
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF :NEW.user_id IS NULL THEN
        SELECT users_seq.NEXTVAL INTO :NEW.user_id FROM dual;
    END IF;
END;
/

-- Blacklist domains table
CREATE TABLE blacklist_domains (
    domain_id NUMBER PRIMARY KEY,
    domain_name VARCHAR2(255) NOT NULL UNIQUE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE SEQUENCE blacklist_domains_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_blacklist_domains
BEFORE INSERT ON blacklist_domains
FOR EACH ROW
BEGIN
    IF :NEW.domain_id IS NULL THEN
        SELECT blacklist_domains_seq.NEXTVAL INTO :NEW.domain_id FROM dual;
    END IF;
END;
/

-- Phishing emails table
CREATE TABLE phishing_emails (
    email_id NUMBER PRIMARY KEY,
    user_id NUMBER NOT NULL,
    sender_email VARCHAR2(255) NOT NULL,
    subject VARCHAR2(255),
    body CLOB,
    risk_score NUMBER DEFAULT 0,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE SEQUENCE phishing_emails_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_phishing_emails
BEFORE INSERT ON phishing_emails
FOR EACH ROW
BEGIN
    IF :NEW.email_id IS NULL THEN
        SELECT phishing_emails_seq.NEXTVAL INTO :NEW.email_id FROM dual;
    END IF;
END;
/

-- Email attachments table
CREATE TABLE email_attachments (
    attachment_id NUMBER PRIMARY KEY,
    email_id NUMBER NOT NULL,
    filename VARCHAR2(255),
    filetype VARCHAR2(50),
    file_size NUMBER,
    FOREIGN KEY (email_id) REFERENCES phishing_emails(email_id)
);

CREATE SEQUENCE email_attachments_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_email_attachments
BEFORE INSERT ON email_attachments
FOR EACH ROW
BEGIN
    IF :NEW.attachment_id IS NULL THEN
        SELECT email_attachments_seq.NEXTVAL INTO :NEW.attachment_id FROM dual;
    END IF;
END;
/

-- Email flags table
CREATE TABLE email_flags (
    flag_id NUMBER PRIMARY KEY,
    email_id NUMBER NOT NULL,
    flagged_by_user NUMBER,
    flag_reason VARCHAR2(255),
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email_id) REFERENCES phishing_emails(email_id),
    FOREIGN KEY (flagged_by_user) REFERENCES users(user_id)
);

CREATE SEQUENCE email_flags_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_email_flags
BEFORE INSERT ON email_flags
FOR EACH ROW
BEGIN
    IF :NEW.flag_id IS NULL THEN
        SELECT email_flags_seq.NEXTVAL INTO :NEW.flag_id FROM dual;
    END IF;
END;
/

-- Email domains table
CREATE TABLE email_domains (
    domain_id NUMBER PRIMARY KEY,
    domain_name VARCHAR2(255) NOT NULL UNIQUE
);

CREATE SEQUENCE email_domains_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_email_domains
BEFORE INSERT ON email_domains
FOR EACH ROW
BEGIN
    IF :NEW.domain_id IS NULL THEN
        SELECT email_domains_seq.NEXTVAL INTO :NEW.domain_id FROM dual;
    END IF;
END;
/


select * from email_domains;