# MetodosAcceso
Notas para levantar un servidor local "The Things Network"

## Pasos para crear un servidor local de The Things Stack con certificados autofirmados.

**Nota**: *Antes de comenzar revisar que no haya ningun servicio utilizando puertos que vamos a necesitar, como por ejemplo que no este mosquitto corriendo como systemctl, o telegraf formateando protocolos mqtt y realizando publicaciones (ya que las va q querer recibir el servidor de TTN y va a dar error por el nombre id de la aplicacion), o tambien node-red. Si alguno se tiene corriendo en la pc host, finalizarlos con:*
```
sudo systemctl stop (nombre del servicio)
```

```
sudo systemctl disable (nombre del servicio)
```

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

### 2. Se siguió el tutorial de la [página web de TTN](https://www.thethingsindustries.com/docs/enterprise/docker/configuration/)

### 3. Descargar los dos archivos Open source `.yml` de la página y editarlos, configurarlos así (o directamente bajar estos dos):

`docker-compose.yml`: [ver documento](archivos/docker-compose.yml)

y el arvhivo `ttn-lw-stack-docker.yml`: [ver documento](archivos/ttn-lw-stack-docker.yml)

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
**Nota**: *Recuerde reemplazar `thethings.example.com` con la dirección de su servidor!*

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
**Nota**: *Esto es para que cambie el grupo y usuario que accede a estos dos archivos, 886 es el grupo y usuario que crea el docker-compose.yml*

### 7. Proceso en la parte de Docker:
Una vez tengamos los certificados y los archivos con la correspondiente estructura de directorios se sigue con los siguientes pasos:
```
sudo docker-compose pull
```
- Inicializar la base de datos del servidor de identidad:
```
sudo docker-compose run --rm stack is-db migrate
```
***
- Crear el usuario admin:
```
sudo docker-compose run --rm stack is-db create-admin-user --id admin --email admin@192.168.100.9
```
**Nota**: *No toma todas las contraseñas, `Admin1` la toma bien. Usar alguna parecida o esa misma.*
***
- Crear el cliente OAuth:

```
sudo docker-compose run --rm stack is-db create-oauth-client \
  --id cli \
  --name "Command Line Interface" \
  --owner admin \
  --no-secret \
  --redirect-uri "local-callback" \
  --redirect-uri "code"
```
***
- Crear un cliente OAuth para la consola (reemplace con su SERVER_ADDRESSY Consola CLIENT_SECRET):
```
SERVER_ADDRESS=https://192.168.100.9
ID=console
NAME=Console
CLIENT_SECRET=console
REDIRECT_URI=${SERVER_ADDRESS}/console/oauth/callback
REDIRECT_PATH=/console/oauth/callback
LOGOUT_REDIRECT_URI=${SERVER_ADDRESS}/console
LOGOUT_REDIRECT_PATH=/console
sudo docker-compose run --rm stack is-db create-oauth-client \
  --id ${ID} \
  --name "${NAME}" \
  --owner admin \
  --secret "${CLIENT_SECRET}" \
  --redirect-uri "${REDIRECT_URI}" \
  --redirect-uri "${REDIRECT_PATH}" \
  --logout-redirect-uri "${LOGOUT_REDIRECT_URI}" \
  --logout-redirect-uri "${LOGOUT_REDIRECT_PATH}"
```
***
- Y luego para el NOC (reemplace con su SERVER_ADDRESSY NOC CLIENT_SECRET):
```
SERVER_ADDRESS=https://192.168.100.9
ID=noc
NAME="Network Operations Center"
CLIENT_SECRET=noc
REDIRECT_URI=${SERVER_ADDRESS}/noc/oauth/callback
REDIRECT_PATH=/noc/oauth/callback
LOGOUT_REDIRECT_URI=${SERVER_ADDRESS}/noc
LOGOUT_REDIRECT_PATH=/noc
sudo docker-compose run --rm stack is-db create-oauth-client \
  --id ${ID} \
  --name "${NAME}" \
  --owner admin \
  --secret "${CLIENT_SECRET}" \
  --redirect-uri "${REDIRECT_URI}" \
  --redirect-uri "${REDIRECT_PATH}" \
  --logout-redirect-uri "${LOGOUT_REDIRECT_URI}" \
  --logout-redirect-uri "${LOGOUT_REDIRECT_PATH}"
```
***
- Iniciar los servicios:
```
docker compose up -d
```

**Nota**: *Esperar a que los 3 dockers esten corriendo, el docker stack demora un minuto en activarse bien.*
***
Una vez hecho todo esto debería estar funcionando bien el servidor localmente en docker. Entrar al navegador Web y dirigirse a la url:

`https://[ip-de-la-pc-host]/console`

Va a mostrar que la página no es segura, permitir en configuración avanzada. Una vez en la interfaz web de TTN, poner como usuario `admin` y la contraseña que se escribió, por ejemplo `Admin1`.
