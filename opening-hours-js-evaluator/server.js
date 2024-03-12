const express = require('express');
const bodyParser = require('body-parser');
const opening_hours = require('opening_hours');
const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());

app.post('/validate', (req, res) => {
    const { strings, verbose, nominatim_object } = req.body; // Now also expecting an optional 'nominatim_object'
    const results = [];

    if (Array.isArray(strings)) {
        strings.forEach(string => {
            try {
                // Check if 'nominatim_object' is provided and is an object
                if (nominatim_object && typeof nominatim_object === 'object') {
                    // Pass 'nominatim_object' as a parameter
                    new opening_hours(string, nominatim_object);
                } else {
                    // Create 'opening_hours' object without 'nominatim_object'
                    new opening_hours(string);
                }

                if (verbose) {
                    results.push({ success: true });
                } else {
                    results.push('1');
                }
            } catch (error) {
                if (verbose) {
                    results.push({ success: false, error: error.toString() });
                } else {
                    results.push('0');
                }
            }
        });
    }

    if (verbose) {
        res.json(results); // Send JSON response in verbose mode
    } else {
        res.send(results.join(' ') + '\n'); // Send plain text response for non-verbose mode
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
