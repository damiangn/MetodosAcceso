# MetodosAcceso
Notas para levantar un servidor local "The Things Nwetwork"

## Pasos para crear un servidor local de The Things Stack con certificados autofirmados.

### 1. Instalar `cfssl`:

* Descargar el archivo binario:
```
wget https://github.com/cloudflare/cfssl/releases/download/v1.6.1/cfssl_linux-amd64 -O cfssl

wget https://github.com/cloudflare/cfssl/releases/download/v1.6.1/cfssljson_linux-amd64 -O cfssljson
```
* Dar permisos de ejecución:
```
chmod +x cfssl cfssljson
```
* Mover los archivos a una ubicación en el PATH:
```
sudo mv cfssl cfssljson /usr/local/bin/
```
* Verificar que esté instalado:
```
cfssl version
```

### 2. Descargar los dos archivos `.yml` de la [página web:](https://www.thethingsindustries.com/docs/enterprise/docker/configuration/)

### 3. Configurarlos así:

`docker-compose.yml`:
```bash
version: '3.7'
services:

  postgres:
    # In production, replace 'latest' with tag from https://hub.docker.com/_/postgres?tab=tags
    image: postgres:17
    restart: unless-stopped
    environment:
      - POSTGRES_PASSWORD=root
      - POSTGRES_USER=root
      - POSTGRES_DB=ttn_lorawan
    volumes:
      - ${DEV_DATA_DIR:-.env/data}/postgres:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"

  redis:
    # In production, replace 'latest' with tag from https://hub.docker.com/_/redis?tab=tags
    image: redis:7.2
    command: redis-server --appendonly yes
    restart: unless-stopped
    volumes:
      - ${DEV_DATA_DIR:-.env/data}/redis:/data
    ports:
      - "127.0.0.1:6379:6379"

  stack:
    # In production, replace 'latest' with tag from https://hub.docker.com/r/thethingsnetwork/lorawan-stack/tags
    image: thethingsnetwork/lorawan-stack:3.34.3
    entrypoint: ttn-lw-stack -c /config/ttn-lw-stack-docker.yml
    command: start
    restart: unless-stopped
    depends_on:
      - redis
      - postgres
    volumes:
      - ./blob:/srv/ttn-lorawan/public/blob
      - ./config/stack:/config:ro
      # If using Let's Encrypt:
      - ./acme:/var/lib/acme
    environment:
      TTN_LW_BLOB_LOCAL_DIRECTORY: /srv/ttn-lorawan/public/blob
      TTN_LW_REDIS_ADDRESS: redis:6379
      TTN_LW_IS_DATABASE_URI: postgres://root:root@postgres:5432/ttn_lorawan?sslmode=disable

    ports:
      # If deploying on a public server:
      - "80:1885"
      - "443:8885"
      - "1881:1881"
      - "8881:8881"
      - "1882:1882"
      - "8882:8882"
      - "1883:1883"
      - "8883:8883"
      - "1884:1884"
      - "8884:8884"
      - "1885:1885"
      - "8885:8885"
      - "1886:1886"
      - "8886:8886"
      - "1887:1887"
      - "8887:8887"
      - "8889:8889"
      - "1700:1700/udp"

    # If using custom certificates:
    secrets:
      - ca.pem
      - cert.pem
      - key.pem

# If using custom certificates:
secrets:
  ca.pem:
    file: ./ca.pem
  cert.pem:
    file: ./cert.pem
  key.pem:
    file: ./key.pem
```

y el arvhivo `ttn-lw-stack-docker.yml`:

```bash
# Identity Server configuration
# Email configuration for "192.168.100.9"
is:
  email:
    sender-name: "The Things Stack"
    sender-address: "noreply@192.168.100.9"
    network:
      name: "The Things Stack"
      console-url: "https://192.168.100.9/console"
      identity-server-url: "https://192.168.100.9/oauth"

    # If sending email with Sendgrid
    # provider: sendgrid
    # sendgrid:
    #   api-key: '...'              # enter Sendgrid API key

    # If sending email with SMTP
    # provider: smtp
    # smtp:
    #   address:  '...'             # enter SMTP server address
    #   username: '...'             # enter SMTP server username
    #   password: '...'             # enter SMTP server password

  # Web UI configuration for "192.168.100.9":
  oauth:
    ui:
      canonical-url: "https://192.168.100.9/oauth"
      is:
        base-url: "https://192.168.100.9/api/v3"

# HTTP server configuration
http:
  cookie:
    block-key: "" # generate 32 bytes (openssl rand -hex 32)
    hash-key: "" # generate 64 bytes (openssl rand -hex 64)
  metrics:
    password: "metrics" # choose a password
  pprof:
    password: "pprof" # choose a password

# If using custom certificates:
tls:
  source: file
  root-ca: /run/secrets/ca.pem
  certificate: /run/secrets/cert.pem
  key: /run/secrets/key.pem

# Let's encrypt for "192.168.100.9"
# tls:
#   source: acme
#   acme:
#     dir: /var/lib/acme
#     email: "you@192.168.100.9"
#     hosts: ["192.168.100.9"]
#     default-host: "192.168.100.9"

# If Gateway Server enabled, defaults for "192.168.100.9":
gs:
  mqtt:
    public-address: "192.168.100.9:1882"
    public-tls-address: "192.168.100.9:8882"
  mqtt-v2:
    public-address: "192.168.100.9:1881"
    public-tls-address: "192.168.100.9:8881"

# If Gateway Configuration Server enabled, defaults for "192.168.100.9":
gcs:
  basic-station:
    default:
      lns-uri: "wss://192.168.100.9:8887"

# Web UI configuration for "192.168.100.9":
console:
  ui:
    canonical-url: "https://192.168.100.9/console"
    account-url: "https://192.168.100.9/oauth"
    is:
      base-url: "https://192.168.100.9/api/v3"
    gs:
      base-url: "https://192.168.100.9/api/v3"
    ns:
      base-url: "https://192.168.100.9/api/v3"
    as:
      base-url: "https://192.168.100.9/api/v3"
    js:
      base-url: "https://192.168.100.9/api/v3"
    gcs:
      base-url: "https://192.168.100.9/api/v3"
    qrg:
      base-url: "https://192.168.100.9/api/v3"
    edtc:
      base-url: "https://192.168.100.9/api/v3"
    dcs:
      base-url: "https://192.168.100.9/api/v3"
  oauth:
    authorize-url: "https://192.168.100.9/oauth/authorize"
    token-url: "https://192.168.100.9/oauth/token"
    logout-url: "https://192.168.100.9/oauth/logout"
    client-id: "console"
    client-secret: "console" # choose or generate a secret

# If Application Server enabled, defaults for "192.168.100.9":
as:
  mqtt:
    public-address: "192.168.100.9:1883"
    public-tls-address: "192.168.100.9:8883"
  webhooks:
    downlink:
      public-address: "192.168.100.9:1885/api/v3"

# Managed gateway configuration, defaults for "192.168.100.9".
# This configures a connection with The Things Gateway Controller, a service operated by The Things Industries.
# This allows connecting, for example, The Things Indoor Gateway Pro.
ttgc:
  enabled: true
  domain: 192.168.100.9
  # Let's Encrypt:
  # tls:
  #   source: acme
  # If using custom certificates:
  tls:
    source: file
    certificate: /run/secrets/cert.pem
    key: /run/secrets/key.pem
```

Reemplazar la dirección IP por la de la PC host donde se quiera instalar el servidor.

### 4. Crear la siguiente estructura de directorios:
```
docker-compose.yml
config/
└── stack/
    └── ttn-lw-stack-docker.yml
```

### 5. Generar los certificados autofirmados:
Crear un archivo llamado `ca.json`, escribir esto dentro de este archivo:
```
{
  "names": [
    {
      "C": "NL",
      "ST": "Noord-Holland",
      "L": "Amsterdam",
      "O": "The Things Demo"
    }
  ]
}
```
* A continuación, utilice el siguiente comando para generar la clave CA y el certificado:
```
cfssl genkey -initca ca.json | cfssljson -bare ca
```
Ahora crear un archivo llamado `cert.json`, escriba la configuración de su certificado:
```
{
  "hosts": ["thethings.example.com"],
  "names": [
    {
      "C": "NL",
      "ST": "Noord-Holland",
      "L": "Amsterdam",
      "O": "The Things Demo"
    }
  ]
}
```
**Nota**: Recuerde reemplazar `thethings.example.com` con la dirección de su servidor!

* Luego, ejecute el siguiente comando para generar la clave del servidor y el certificado:
```
cfssl gencert -ca ca.pem -ca-key ca-key.pem cert.json | cfssljson -bare cert
```
Los siguientes pasos suponen que la clave de certificado se llama key.pem, así que tendrás que cambiar el nombre `cert-key.pem` a `key.pem`. Para esto escribir:
```
mv cert-key.pem key.pem
```
Al final, su directorio debe verse así:
```
cert.pem
key.pem
ca.pem
docker-compose.yml          # defines Docker services for running The Things Stack
config/
└── stack/
    └── ttn-lw-stack-docker.yml    # configuration file for The Things Stack
```
### 6. Para utilizar el certificado `(cert.pem)` y clave `(key.pem)`, también necesita establecer estos permisos:
```
sudo chown 886:886 ./cert.pem ./key.pem
```
**Nota**: Esto es para que cambie el grupo y usuario que accede a estos dos archivos, 886 es el grupo y usuario que crea el docker-compose.yml

### 7. Proceso en la parte de Docker:
Una vez tengamos los certificados y los archivos con la correspondiente estructura de directorios se sigue con los siguientes pasos:
```
sudo docker-compose pull
```
Inicializar la base de datos del servidor de identidad:
```
sudo docker-compose run --rm stack is-db migrate
```
Crear el usuario admin:
```
sudo docker-compose run --rm stack is-db create-admin-user --id admin --email admin@192.168.100.9
```
Crear el cliente OAuth:

```
sudo docker-compose run --rm stack is-db create-oauth-client --id console --name "Console" --owner admin --no-secret --redirect-uri "https://192.168.100.9/console/oauth/callback" --redirect-uri "/console/oauth/callback"
```
(Opcional) Crear cliente OAuth CLI (para gestionar desde consola y no desde interfaz web):
```
docker compose run --rm stack is-db create-oauth-client --id cli --name "Command Line Interface" --owner admin --no-secret --redirect-uri "local-callback" --redirect-uri "code"
```
Iniciar los servicios:
```
docker compose up -d
```
