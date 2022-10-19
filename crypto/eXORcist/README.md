# eXORcist

## Write-up

The solution for the challenge is pretty simple, the server receives the text and place the flag randomly inside it, then generate a key and xor with the text.  

The challenges is therefore vulnerable to the repeated key attack. The first step would be to get the key by sending a long text with known caracters, the result is xored with the sent text in order to get the key, and decrypt the flag part.
