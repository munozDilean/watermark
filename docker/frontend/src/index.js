const app = require('express')();

// ROUTES

app.get('/', (req, res) => {        //get requests to the root ("/") will route here
    res.sendFile('index.html', {root: __dirname});      //server responds by sending the index.html file to the client's browser
                                                        //the .sendFile method needs the absolute path to the file, see: https://expressjs.com/en/4x/api.html#res.sendFile 
});

// Port to listen

const port = process.env.PORT || 8080;

// Start app

app.listen(port, ()=> console.log(`app listening on http://localhost:${port}`));