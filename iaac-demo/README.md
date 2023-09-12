[<img src="https://em-content.zobj.net/thumbs/120/openmoji/338/flag-united-states_1f1fa-1f1f8.png" alt="us flag" width="48"/>](./README_en.md)

# Introdução

Este projeto Terraform permite criar uma infraestrutura mínima com o 
propósito de testar o EC2 Instance Connect Endpoint.

Será criada 1 VPC com 3 subnets privadas e 3 públicas. 
Alguns segurity groups e 3 instâncias EC2, sendo uma para cada subnet
privada, além da instância do EC2 Instance Connect Endpoint.


# Terraform

Terraform é tecnologia para uso de infraestrutura como código (IaaC), assim como Cloudformation da AWS. 

Porém com Terraform é possível definir infraestrutura para outras clouds como GCP e Azure.

## Instalação

Para utilizar é preciso baixar o arquivo do binário compilado para o sistema que você usa. Acesse https://www.terraform.io/downloads

## Iniciaizando o repositório

É preciso inicializar o Terraform na raiz deste projeto executando 

```
terraform init
```

## Definindo credenciais

O arquivo de definição do Terraform é o *main.tf*.

É nele que especificamos como nossa infraestrutura será.

É importante observar que no bloco do ``provider "aws"`` é onde definimos que vamos usar Terraform com AWS. 

```
provider "aws" {
  region = "us-east-1"
  profile = "meu-profile"
}
```

Como Terraform cria toda a infra automaticamente na AWS, é preciso dar permissão para isso por meio de credenciais.

Apenar se ser possível especificar as chaves no próprio provider, esta abordagem não é indicada. Principalmente por este código estar em um repositório git, pois que tiver acesso ao repositório saberá qual são as credenciais.

Uma opção melhor é usar um *profile* da AWS configurado localmente. 

Aqui usamos o profile chamado *projeto*. Para criar um profile execute o comando abaixo usando o AWS CLI e preencha os parâmetros solicitados.

```
aws configure --profile meu-projeto
```

## Variáveis - Configurações adicionais 

Além da configuração do profile será preciso definir algumas variáveis.

Para evitar expor dados sensíveis no git, como senha do banco de dados, será preciso copiar o arquivo ``terraform.tfvars.exemplo`` para ``terraform.tfvars``.

No arquivo ``terraform.tfvars`` redefina os valores das variáveis. Perceba que será necessário ter um domínio já no Route53 caso deseje usar um domínio e não apenas acessar via url do LoadBalancer.

Todas as variáveis possíveis para este arquivo podem ser vistas no arquivo ``variables.tf``. Apenas algumas delas foram utilizadas no exemplo.

## Aplicando a infra definida

O Terraform provê alguns comandos básicos para planejar, aplicar e destroir a infraestrutura. 

Ao começar a aplicar a infraestrutura, o Terraform cria o arquivo ``terraform.tfstate``, que deve ser preservado e não deve ser alterado manualmente.

Por meio deste arquivo o Terraform sabe o estado atual da infraestrutura e é capar de adicionar, alterar ou remover recursos.

Neste repositório não estamos versionando este arquivo por se tratar de um repositório compartilhado e para estudo. Em um repositório real possívelmente você vai querer manter este arquivo preservado no git.

###  Verificando o que será criado, removido ou alterado
```
terraform plan
```

###  Aplicando a infraestrutura definida
```
terraform apply
```
ou, para confirmar automáticamente.
```
terraform apply --auto-approve
```

###  Destruindo toda sua infraestrutura

<font color="red">
  <span><b>CUIDADO!</b><br>
  Após a execução dos comandos abaixo você perderá tudo que foi especificado no seu arquivo Terraform (banco de dados, EC2, EBS etc).</span>.
</font>

```
terraform destroy
```
ou, para confirmar automáticamente.
```
terraform destroy --auto-approve
```

# Considerações finais

Este é um projeto para experimentações e estudo do Terraform. 
Mesmo proporcionando a criação dos recursos mínimos para execução do projeto na AWS, é desaconselhado o uso deste projeto para implantação de cargas de trabalho em ambiente produtivo.

# Referências

1. [Terraform](https://www.terraform.io/)
