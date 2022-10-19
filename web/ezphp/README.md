# ezphp

## Write-up

- **PHP 5.3** doesn't handle `HEAD` requests correctly
- So the solution is to first send a `HEAD` request to `/index.php`
- It will set `SESSION[admin]` to `1` and stop before setting it back to `0`
- Then send another GET request with the same session and you will get the flag
