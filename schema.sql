-- ================================================================
-- Cloud Computing Quiz System - Database Schema
-- Run this file in MySQL to set up the database
-- ================================================================

CREATE DATABASE IF NOT EXISTS cloud_quiz_db;
USE cloud_quiz_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_option ENUM('A', 'B', 'C', 'D') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quiz attempts table
CREATE TABLE IF NOT EXISTS attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    total INT NOT NULL,
    taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Seed Data ─────────────────────────────────────────────────────────────────

-- Default admin account (password: admin123)
INSERT INTO users (username, password, role) VALUES
('admin', SHA2('admin123', 256), 'admin');

-- Sample Cloud Computing Questions
INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_option) VALUES
('What does IaaS stand for in cloud computing?',
 'Internet as a Service', 'Infrastructure as a Service', 'Integration as a Service', 'Information as a Service', 'B'),

('Which of the following is NOT a major cloud service provider?',
 'Amazon Web Services', 'Microsoft Azure', 'Google Cloud Platform', 'Oracle Linux', 'D'),

('What is the primary benefit of cloud elasticity?',
 'Fixed pricing', 'Automatic scaling based on demand', 'Manual resource management', 'Local data storage', 'B'),

('Which cloud deployment model is exclusively used by a single organization?',
 'Public Cloud', 'Hybrid Cloud', 'Private Cloud', 'Community Cloud', 'C'),

('What does SaaS stand for?',
 'Storage as a Service', 'Security as a Service', 'Software as a Service', 'System as a Service', 'C'),

('Which AWS service is used for object storage?',
 'EC2', 'RDS', 'S3', 'Lambda', 'C'),

('What is serverless computing?',
 'Computing without any servers', 'Cloud execution without managing server infrastructure', 'Offline computing', 'Local server computing', 'B'),

('In cloud computing, what is a "region"?',
 'A country boundary', 'A geographic area with multiple data centers', 'A virtual network segment', 'A type of storage class', 'B'),

('What does CDN stand for?',
 'Cloud Data Network', 'Content Delivery Network', 'Central Distribution Node', 'Cloud Deployment Node', 'B'),

('Which of the following best describes multi-tenancy in cloud computing?',
 'One server per customer', 'Multiple customers share the same physical infrastructure', 'Multiple servers for one customer', 'Dedicated hardware per application', 'B'),

('What is the purpose of a load balancer in cloud architecture?',
 'Store large amounts of data', 'Distribute traffic across multiple servers', 'Encrypt network traffic', 'Monitor server performance', 'B'),

('Which cloud service model gives the most control to the user?',
 'SaaS', 'PaaS', 'IaaS', 'FaaS', 'C');