CREATE TABLE IF NOT EXISTS jobs (
    job_id       INT PRIMARY KEY,
    title        VARCHAR(120) NOT NULL,
    role         VARCHAR(80)  NOT NULL,
    company      VARCHAR(120) NOT NULL,
    location     VARCHAR(80)  NOT NULL,
    salary_lpa   DECIMAL(6,1),
    exp_min      INT,
    exp_max      INT,
    education    VARCHAR(40),
    description  TEXT,
    posted_date  DATE NOT NULL,
    source       VARCHAR(20) DEFAULT 'seed',
    INDEX idx_role (role), INDEX idx_location (location), INDEX idx_posted (posted_date)
);
CREATE TABLE IF NOT EXISTS job_skills (
    job_id  INT NOT NULL,
    skill   VARCHAR(60) NOT NULL,
    is_core TINYINT NOT NULL DEFAULT 1,
    PRIMARY KEY (job_id, skill),
    INDEX idx_skill (skill),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(80)  NOT NULL,
    email         VARCHAR(190) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    salt          VARCHAR(64)  NOT NULL,
    created_at    VARCHAR(30),
    profile_json  MEDIUMTEXT
);
CREATE TABLE IF NOT EXISTS resume_skills (
    user_id  INT NOT NULL,
    skill    VARCHAR(60) NOT NULL,
    strength INT,
    PRIMARY KEY (user_id, skill)
);
CREATE TABLE IF NOT EXISTS applications (
    user_id     INT NOT NULL,
    job_id      INT NOT NULL,
    match_score DECIMAL(5,4),
    status      VARCHAR(20) DEFAULT 'Saved',
    saved_at    VARCHAR(30),
    PRIMARY KEY (user_id, job_id)
);
CREATE TABLE IF NOT EXISTS feed_events (
    event_id   INT AUTO_INCREMENT PRIMARY KEY,
    created_at VARCHAR(30),
    kind       VARCHAR(20),
    message    VARCHAR(400)
);
