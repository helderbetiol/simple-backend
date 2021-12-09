# Simple Backend - 2a Avaliação

A aplicação flask para responder requisições HTTP com o IP do servidor implementada para a 1a Avaliação foi extendida para incluir as implementações da 2a Avaliação, que estão divididas segundo o branch:
- *main*: relógio de Lamport;
- *mutual_exclusion*: algoritmo de Lamport para exclusão mútua, aprimorado por Ricart e Agrawala; 
- *bully*: algoritmo do valentão (bully) de eleição

Vale notar que, apesar de dividido em branches para testes na cloud, o branch seguinte inclui também o código do branch precedente, ou seja, *mutual_exclusion* inclui o código do relógio de Lamport e *bully* inclui ambos. Logo, para avaliar o código de todos os algoritmos, pode-se usar apenas o branch *bully*.

Seguem instruções de como instalar e executar a aplicação em uma máquina virtual AWS:

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
* Um arquivo .env com a variável de ambiente MY_PID foi adicionado ao diretório local com um valor padrão 1. Para que a comunicação funcione corretamente, cada aplicação em execução deve ter um valor diferente para esta variável. Altere para um valor númerico único em cada máquina virtual onde a aplicação foi instalada antes de executá-la. Para o branch mutual_exclusion, também é necessário atualizar a variável MAX_PID do mesmo arquivo com o número de aplicações que serão executadas simultaneamente:
```terminal
vi .env
```

### Execute a aplicação
* Utilise flask:
```terminal
sudo flask run --host=0.0.0.0 --port=80
```

## Como usar a aplicação

Para todas as versões, a aplicação responderá requisições HTTP GET direcionadas à porta 80 deste servidor no caminho raíz "/" com uma mensagem contendo o IP do servidor onde está executando. Demais requisições possíveis segundo versão:

### Branch main
- POST em /lamport/send: solicita ao processo um novo evento local ou de envio de mensagem. O body da requisição deve ser do tipo JSON e conter os campos a seguir:
```
{
    "destination_id": 1
}
```
O valor de destination_id corresponde ao PID para o qual a mensagem deve ser enviada. Se é o mesmo PID to processo para o qual o POST é feito, um evento local se produz.

- GET em /lamport/status: retornará informações do estado do processo. Exemplo de resposta:
```
{
    "CLOCK": 1,
    "PID": 1
}
```

### Branch mutual_exclusion
Além das requisições da branch main:
- POST em /lamport/critical: solicita ao processo que acesse região crítica pedindo permissão aos demais processos. Caso já esteja acessando a região crítica, interrompe e retorna ao estado sem acesso. O body da requisição deve ser do tipo JSON e conter os campos a seguir:
```
{
    "destination_id": all
}
```
