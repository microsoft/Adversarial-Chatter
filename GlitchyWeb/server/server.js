require('dotenv').config();
const express = require('express');
const sql = require('mssql');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const { body, validationResult } = require('express-validator');

const app = express();
app.use(express.json());
app.use(cors());

const dbConfig = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  server: process.env.DB_SERVER,
  database: process.env.DB_NAME,
  options: { encrypt: true, trustServerCertificate: false },
};

// Registration Route
app.post(
  '/api/register',
  [
    body('username').notEmpty().withMessage('Username is required'),
    body('email').isEmail().withMessage('Invalid email'),
    body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
  ],
  async (req, res) => {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      // Hash the password before storing
      const hashedPassword = await bcrypt.hash(req.body.password, 10);

      let FullName = req.body.firstname + ' ' +  req.body.lastname

      let pool = await sql.connect(dbConfig);
      let result = await pool.request()
        .input('FullName', sql.NVarChar, FullName) 
        .input('PreferredName', sql.NVarChar, req.body.username)
        .input('IsPermittedToLogon', sql.Bit, 1)
        .input('IsExternalLogonProvider', sql.Bit, 0)
        .input('IsSystemUser', sql.Bit, 1)
        .input('IsEmployee', sql.Bit, 1)
        .input('IsSalesperson', sql.Bit, 0)
        .input('EmailAddress', sql.NVarChar, req.body.email)
        .input('HashedPassword', sql.NVarChar, hashedPassword) // Store hashed password
        .input('LastEditedBy', sql.BigInt, 1)
        .query('INSERT INTO Application.People (FullName, PreferredName, IsPermittedToLogon, IsExternalLogonProvider, HashedPassword, IsSystemUser, IsEmployee , IsSalesperson, EmailAddress, LastEditedBy)' +
           'VALUES (@FullName, @PreferredName, @IsPermittedToLogon, @IsExternalLogonProvider, CONVERT(VARBINARY(MAX), @HashedPassword), @IsSystemUser, @IsEmployee , @IsSalesperson, @EmailAddress, @LastEditedBy)');

      res.status(201).json({ message: 'User registered successfully' });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });


  // Login Route
  app.post(
    '/api/login',
    [
      body('username').notEmpty().withMessage('Username is required'),
      body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
    ],
    async (req, res) => {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }
  
      try {
        let pool = await sql.connect(dbConfig);
        let result = await pool.request()
          .input('PreferredName', sql.NVarChar, req.body.username)
          .query('SELECT HashedPassword FROM Application.People WHERE PreferredName = @PreferredName');
        
        let enteredPassword = req.body.password;

        if (result.recordset.length === 0) {
          return res.status(401).json({ message: 'Invalid username or password' }); // Unauthorized
        }
  
        const storedHashedPassword = result.recordset[0].HashedPassword;
  
        // Convert stored hash from Buffer to a string before comparing
        const hashedPasswordString = storedHashedPassword.toString('utf-8');
  
        // Compare the entered password with the stored hash
        const isMatch = await bcrypt.compare(enteredPassword, hashedPasswordString);
  
        if (isMatch) {
          return res.status(200).json({ message: 'Login successful' + ' entered - '+   enteredPassword + ' hashedPWD string' + hashedPasswordString }); // Send success response
        } else {
          return res.status(401).json({ message: 'Invalid username or password' + ' entered - '+   enteredPassword + ' hashedPWD string' + hashedPasswordString });
        }
  
      } catch (error) {
        console.error('Error verifying password:', error);
        return res.status(500).json({ error: error.message });
      }
    }
  );

// Blog Route
app.get('/api/blogs', async (req, res) => {
  try {
    let pool = await sql.connect(dbConfig);
    let result = await pool.request().query('SELECT id, title, content, author, publish_date FROM Application.BlogPosts');

    if (result.recordset.length === 0) {
      return res.status(404).json({ message: 'No blogs found' });
    }

    return res.status(200).json(result.recordset);
  } catch (error) {
    console.error('Error retrieving blogs:', error);
    return res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));

