// Enhanced demo file to show how the security scanner adds detailed comments with fixes.
// This file contains intentional vulnerabilities for demonstration.

const express = require('express');
const mysql = require('mysql');
const app = express();

// This will get a detailed security comment with fix above it
const DATABASE_PASSWORD = "admin123";

// This will get a detailed security comment with fix above it
const API_KEY = "sk-1234567890abcdef";

function getUserById(userId) {
    // This will get a detailed security comment with fix above it
    const query = `SELECT * FROM users WHERE id = ${userId}`;
    return query;
}

function pingHost(host) {
    const { exec } = require('child_process');
    // This will get a detailed security comment with fix above it
    exec(`ping -c 1 ${host}`, (error, stdout, stderr) => {
        return stdout;
    });
}

function readFile(filename) {
    const fs = require('fs');
    // This will get a detailed security comment with fix above it
    return fs.readFileSync(filename, 'utf8');
}

app.get('/search', (req, res) => {
    const query = req.query.q || '';
    // This will get a detailed security comment with fix above it
    const html = `<h1>Search Results for: ${query}</h1>`;
    res.send(html);
});

function loadUserData(data) {
    // This will get a detailed security comment with fix above it
    return eval(data);
}

function hashPassword(password) {
    const crypto = require('crypto');
    // This will get a detailed security comment with fix above it
    return crypto.createHash('md5').update(password).digest('hex');
}

// This will get a detailed security comment with fix above it
app.set('debug', true);

function generateToken() {
    // This will get a detailed security comment with fix above it
    return Math.floor(Math.random() * 9000) + 1000;
}

app.get('/error', (req, res) => {
    const error = req.query.error || '';
    // This will get a detailed security comment with fix above it
    res.status(500).send(`Error occurred: ${error}`);
});

// This will get a detailed security comment with fix above it
app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on port 5000');
}); 