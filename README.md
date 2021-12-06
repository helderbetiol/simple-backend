# Simple Backend

Uma simples aplicação flask para responder requisições HTTP com o IP do servidor onde está executando. Seguem instruções de como instalar e executar a aplicação em uma máquina virtual AWS:

## Preparar a VM

### Logar na máquina virtual 
* Após criar uma VM ubuntu com configurações mínimas e criar um par de chaves de acesso, utilise ssh para acessar a VM:
```terminal
ssh -i [nome do arquivo da chave privada].pem ubuntu@[DNS IPv4 público]
```

### Instalar pip
* Python 3 já estará instalado na VM. Instale pip para, em seguida, instalar os requisitos da aplicação:
```terminal
sudo apt update
sudo apt install python3-pip
```

## Instalar e executar a aplicação

### Obter o código deste repositório
* Clone o repositório usando o comando git:
```terminal
git clone https://github.com/helderbetiol/simple-backend.git
```

### Instalar os requisitos:
* Execute o comando pip no diretório criado ao clonar o repositório:
```terminal
cd simple-backend/
sudo pip install -r requirements.txt
```

### Configure um PID único
* Um arquivo .env com a variável de ambiente MY_PID foi adicionado ao diretório local com um valor padrão 1. Para que a comunicação funcione corretamente, cada aplicação em execução deve ter um valor diferente para esta variável. Altere para outro valor númerico em cada máquina virtual onde a aplicação foi instalada antes de executá-la:
```terminal
vi .env
```

### Execute a aplicação
* Utilise flask:
```terminal
sudo flask run --host=0.0.0.0 --port=80
```

A aplicação responderá requisições HTTP GET direcionadas à porta 80 deste servidor no caminho raíz "/" com uma mensagem contendo o IP do servidor onde está executando.