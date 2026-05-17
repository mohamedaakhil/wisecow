#!/usr/bin/env bash

SRVPORT=${PORT:-4499}
RSPFILE=response
TLS_CERT=${TLS_CERT:-/certs/tls.crt}
TLS_KEY=${TLS_KEY:-/certs/tls.key}

rm -f $RSPFILE
mkfifo $RSPFILE

get_api() {
    read line
    echo $line
}

handleRequest() {
    get_api
    mod=$(fortune)
    wisdom=$(cowsay "$mod")
    cat <<EOF > $RSPFILE
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Connection: close

<!DOCTYPE html>
<html>
<head><title>Wisecow</title>
<style>
  body { background: #1a1a2e; color: #e0e0e0; font-family: monospace; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
  pre  { background: #16213e; border: 1px solid #0f3460; border-radius: 8px; padding: 2rem; font-size: 1.1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
</style>
</head>
<body><pre>$wisdom</pre></body>
</html>
EOF
}

prerequisites() {
    command -v cowsay  >/dev/null 2>&1 && \
    command -v fortune >/dev/null 2>&1 || {
        echo "Install prerequisites: cowsay and fortune"
        exit 1
    }
}

main() {
    prerequisites

    # Use socat for TLS if certs exist, otherwise plain netcat
    if [ -f "$TLS_CERT" ] && [ -f "$TLS_KEY" ]; then
        echo "Wisdom served with TLS on port=$SRVPORT..."
        while true; do
            cat $RSPFILE | socat \
                OPENSSL-LISTEN:${SRVPORT},cert=${TLS_CERT},key=${TLS_KEY},verify=0,reuseaddr,fork \
                STDIN | handleRequest
            sleep 0.01
        done
    else
        echo "Wisdom served (plain HTTP) on port=$SRVPORT..."
        while true; do
            cat $RSPFILE | nc -lN $SRVPORT | handleRequest
            sleep 0.01
        done
    fi
}

main
