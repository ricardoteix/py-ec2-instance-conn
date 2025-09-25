import os
import subprocess
import sys
import time

import boto3
import botocore.exceptions

from src.credentials import get_active_credentials

selected_profile = ''
os.environ['ec2-conn-profile'] = selected_profile
connected = False
vpc_id = ''


def describe_vpcs(profile: str):
    try:
        session = boto3.Session(profile_name=profile)
        ec2_client = session.client('ec2')
        response = ec2_client.describe_vpcs()
    except botocore.exceptions.NoRegionError as e:
        print("Erro: Nenhuma região configurada. Verifique suas configurações do AWS CLI.")
        return []
    except boto3.exceptions.ProfileNotFound as e:
        print(f"Erro: O profile '{profile}' não foi encontrado. Verifique se o profile está configurado corretamente.")
        return []
    except Exception as e:
        print(f"Erro ao descrever VPCs: {e}")
        return []

    vpcs = []
    for vpc in response['Vpcs']:
        vpc_name = '-'
        if 'Tags' in vpc:
            for tag in vpc['Tags']:
                if tag['Key'] == 'Name':
                    vpc_name = tag['Value']
        vpcs.append(
            {
                'id': vpc['VpcId'],
                'name': vpc_name
            }
        )
    return vpcs

def describe_instance_connect_endpoints(profile: str, vpc_id: str):
    try:
        session = boto3.Session(profile_name=profile)
        ec2_client = session.client('ec2')
        response = ec2_client.describe_instance_connect_endpoints(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }
            ]
        )
    except botocore.exceptions.NoRegionError as e:
        print("Erro: Nenhuma região configurada. Verifique suas configurações do AWS CLI.")
        return None
    except boto3.exceptions.ProfileNotFound as e:
        print(f"Erro: O profile '{profile}' não foi encontrado. Verifique se o profile está configurado corretamente.")
        return None
    except Exception as e:
        print(f"Erro ao descrever Instance Connect Endpoints: {e}")
        return None

    if 'InstanceConnectEndpoints' in response and response['InstanceConnectEndpoints']:
        return response['InstanceConnectEndpoints'][0]['InstanceConnectEndpointId']
    else:
        return None


def get_vpc_name(ec2_client, vpc_id):
    try:
        response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
        if 'Vpcs' in response and response['Vpcs']:
            vpc = response['Vpcs'][0]
            if 'Tags' in vpc:
                for tag in vpc['Tags']:
                    if tag['Key'] == 'Name':
                        return tag['Value']
    except Exception as e:
        print(f"Error getting VPC name for {vpc_id}: {e}")
    return '-'


def describe_instances(profile: str, vpc_id: str = None):

    try:
        session = boto3.Session(profile_name=profile)
        ec2_client = session.client('ec2')

        filters = [
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                ]
            },
        ]

        if vpc_id:
            filters.append({
                'Name': 'vpc-id',
                'Values': [vpc_id]
            })

        response = ec2_client.describe_instances(
            Filters=filters
        )
    except botocore.exceptions.NoRegionError as e:
        print("Erro: Nenhuma região configurada. Verifique suas configurações do AWS CLI.")
        return []
    except boto3.exceptions.ProfileNotFound as e:
        print(f"Erro: O profile '{profile}' não foi encontrado. Verifique se o profile está configurado corretamente.")
        return []
    except Exception as e:
        print(f"Erro ao descrever instâncias: {e}")
        return []

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            vpc_id = instance['VpcId']
            vpc_name = get_vpc_name(ec2_client, vpc_id)
            instances.append(
                {
                    'id': instance['InstanceId'],
                    'tags': instance['Tags'] if 'Tags' in instance else '',
                    'key_name': instance['KeyName'] if 'KeyName' in instance else '',
                    'vpc_id': vpc_id,
                    'vpc_name': vpc_name,
                    'az': instance['Placement']['AvailabilityZone']
                }
            )

    return instances


def open_terminal(command, win_use_start=True, win_use_keep=False):
    global connected

    if sys.platform.startswith('linux'):
        subprocess.Popen(['xterm', '-e', command])
    elif sys.platform.startswith('darwin'):  # macOS
        os.system(f"osascript -e 'tell app \"Terminal\" to do script \"{command}\"'")
    elif sys.platform.startswith('win'):  # Windows
        if win_use_start:
            command_run = ' '.join(['start', 'cmd', '/k' if win_use_keep else '/c', f'{command}'])
            os.system(command_run)
        else:
            command_run = ' '.join(['cmd', '/k' if win_use_keep else '/c', f'{command}'])
            os.system(command_run)
        connected = True
    else:
        print("Sistema não suportado")


def create_instances_submenu():
    global selected_profile

    instance = list_instances('Conectar à instância')

    if type(instance) == bool and instance:
        return True

    if not instance:
        return False

    instance_id = instance['id']
    key_name = instance['key_name']
    vpc_id = instance['vpc_id']

    print("> Estabelecendo conexão SSH. Aguarde...")
    return f'aws ec2-instance-connect ssh --instance-id {instance_id} --os-user ubuntu --profile {selected_profile}'


def list_instances(new_menu):
    global selected_profile
    global vpc_id

    print("> Listando instâncias. Aguarde...")
    instances = describe_instances(selected_profile, vpc_id)

    while True:
        clear_screen()
        print(f"Menu de Opções -> {new_menu}")
        print("-------------------------------------")
        print("Selecione a instância:")
        options = ""
        for index, instance in enumerate(instances):
            instance_name = '-'
            if instance['tags']:
                for tag in instance['tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']

            print(f"{index + 1}. {instance['id']} [{instance['vpc_name']} - {instance['vpc_id']} - {instance['az']}] ({instance_name})")
            options += f"{index + 1}"

        print(f"{len(instances) + 1}. Voltar ao menu anterior")

        options += f"{len(instances) + 1}"

        choice = input("Escolha uma opção: ")
        if choice not in options and choice != '/q':
            print("-- Opção inválida. Selecione uma das opções possíveis.")
            time.sleep(3)
            return False

        if choice == '/q':
            print("Voltando...")
            return True

        selected_index = int(choice)

        for index, instance in enumerate(instances):
            if selected_index - 1 == index:
                return instance

        if selected_index == len(instances) + 1:
            print("Voltando...")

        return True


def create_credentials_submenu():
    global selected_profile

    # selected_profile = ''

    os.environ['ec2-conn-profile'] = selected_profile

    credentials = get_active_credentials()

    while True:
        clear_screen()
        print("Menu de Opções -> Liberar acesso para RDS")
        print("-------------------------------------")
        print("Selecione o profile que deseja usar:")
        options = ""
        for index, credential in enumerate(credentials):
            print(f"{index + 1}. {credential}")
            options += f"{index + 1}"
        print(f"{len(credentials) + 1}. Voltar ao menu anterior")

        options += f"{len(credentials) + 1}"

        choice = input("Escolha uma opção: ")
        if choice not in options:
            print("-- Opção inválida. Selecione uma das opções possíveis.")
            time.sleep(3)
            return False

        selected_index = int(choice)

        for index, credential in enumerate(credentials):
            if selected_index - 1 == index:
                selected_profile = credential
                return True

        if selected_index == len(credentials) + 1:
            print("Voltando...")

        return True


def select_vpc_submenu():
    global selected_profile
    global vpc_id

    print("> Listando VPCs. Aguarde...")
    vpcs = describe_vpcs(selected_profile)

    while True:
        clear_screen()
        print(f"Menu de Opções -> Selecionar VPC")
        print("-------------------------------------")
        print("Selecione a VPC:")
        options = ""
        for index, vpc in enumerate(vpcs):
            print(f"{index + 1}. {vpc['id']} ({vpc['name']})")
            options += f"{index + 1}"

        print(f"{len(vpcs) + 1}. Voltar ao menu anterior")

        options += f"{len(vpcs) + 1}"

        choice = input("Escolha uma opção: ")
        if choice not in options:
            print("-- Opção inválida. Selecione uma das opções possíveis.")
            time.sleep(3)
            return False

        selected_index = int(choice)

        for index, vpc in enumerate(vpcs):
            if selected_index - 1 == index:
                vpc_id = vpc['id']
                return True

        if selected_index == len(vpcs) + 1:
            print("Voltando...")

        return True

def create_tunnel_submenu():
    global selected_profile
    global vpc_id

    print("> Buscando Instance Connect Endpoint. Aguarde...")
    endpoint_id = describe_instance_connect_endpoints(selected_profile, vpc_id)

    if not endpoint_id:
        print(f"## Nenhum Instance Connect Endpoint encontrado para a VPC {vpc_id}.")
        input("Pressione Enter para continuar...")
        return True

    instance = list_instances('Abrir túnel com EC2 Instance Connect Endpoint')

    if type(instance) == bool and instance:
        return True

    if not instance:
        return False

    instance_id = instance['id']

    print("> Abrindo túnel. Aguarde...")
    command = f'aws ec2-instance-connect open-tunnel --instance-connect-endpoint-id {endpoint_id} --instance-id {instance_id} --remote-port 22 --local-port 22 --profile {selected_profile}'
    open_terminal(command)
    return True


def create_rds_submenu():
    global selected_profile

    instance = list_instances('Liberar acesso para RDS')

    if type(instance) == bool and instance:
        return True

    if not instance:
        return False

    instance_id = instance['id']
    key_name = instance['key_name']
    vpc_id = instance['vpc_id']

    tunel_command = f'aws ec2-instance-connect open-tunnel --instance-id {instance_id} --remote-port 22 --local-port 22 --profile {selected_profile}'
    print("> Abrindo novo terminal com tunel. Mantenha esta janela aberta!")
    print(f"> {tunel_command} ")
    open_terminal(tunel_command)

    print("> Solicitando informações para libera o acesso do RDS: (digite /q para voltar)")
    rds_endpoint = input("Host do RDS: ")
    if rds_endpoint == '/q':
        print("Voltando ao menu principal...")
        return True
    local_port = input("Porta local do RDS: ")
    if local_port == '/q':
        print("Voltando ao menu principal...")
        return True
    remote_port = input("Porta remota do RDS: ")
    if remote_port == '/q':
        print("Voltando ao menu principal...")
        return True
    ec2_key = input(f"Caminho da key da instância ({key_name}): ")
    if ec2_key == '/q':
        print("Voltando ao menu principal...")
        return True
    os_user = input(f"Usuário do SO remoto (ubuntu ou ec2-user): ")
    if os_user == '/q':
        print("Voltando ao menu principal...")
        return True

    rds_endpoint = rds_endpoint.encode(encoding='UTF-8', errors='strict').decode('utf8')

    if os_user == '':
        os_user = 'ubuntu'

    print("> Abrindo novo terminal com portas mapeadas. Mantenha esta janela aberta!")
    map_ssh = f'ssh -i "{ec2_key}" -L {local_port}:{rds_endpoint}:{remote_port} {os_user}@localhost -N -f && pause'
    print(map_ssh)
    open_terminal(map_ssh, win_use_start=True, win_use_keep=True)

    return True


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("""\n#####################################""")
    print("""#### AWS Instance Connect Access ####""")
    print("""#####################################\n""")


def execute_command(command):
    os.system(command)
    input("Pressione Enter para continuar...")


def main():
    global connected
    global vpc_id
    while True:
        clear_screen()
        if selected_profile == '':
            print("[ Nenhum profile selecionado ]")
        else:
            print(f"[ Profile selecionado: {selected_profile} ]")

        if vpc_id != '':
            print(f"[ VPC selecionada: {vpc_id} ]")

        print("Menu de Opções:\n")
        print("1. Selecionar Profile")
        print("2. Selecionar VPC")
        print("3. Conectar à instância")
        print("4. Abrir túnel com EC2 Instance Connect Endpoint")
        print("5. Liberar acesso para RDS")
        print("6. Sair")

        choice = input("\nEscolha uma opção: ")

        if choice == "1":

            valid = create_credentials_submenu()
            while not valid:
                valid = create_credentials_submenu()

        elif choice == "2":
            if selected_profile == '':
                print("## Nenhum profile selecionado. ")
                print("## É preciso selecionar primeiro um profile.")
                input("Pressione Enter para continuar...")
                continue

            valid = select_vpc_submenu()
            while not valid:
                valid = select_vpc_submenu()

        elif choice == "3":

            if selected_profile == '':
                print("## Nenhum profile selecionado. ")
                print("## É preciso selecionar primeiro um profile.")
                input("Pressione Enter para continuar...")
                continue

            if vpc_id == '':
                print("## Nenhuma VPC selecionada. ")
                print("## É preciso selecionar primeiro uma VPC.")
                input("Pressione Enter para continuar...")
                continue

            valid = create_instances_submenu()
            while not valid:
                valid = create_instances_submenu()

            if valid is True:
                continue

            print(valid)
            time.sleep(5)
            open_terminal(valid)

            # if connected:
            #     break

        elif choice == "4":

            if selected_profile == '':
                print("## Nenhum profile selecionado. ")
                print("## É preciso selecionar primeiro um profile.")
                input("Pressione Enter para continuar...")
                continue

            if vpc_id == '':
                print("## Nenhuma VPC selecionada. ")
                print("## É preciso selecionar primeiro uma VPC.")
                input("Pressione Enter for continue...")
                continue

            valid = create_tunnel_submenu()
            while not valid:
                valid = create_tunnel_submenu()

        elif choice == "5":

            if selected_profile == '':
                print("## Nenhum profile selecionado. ")
                print("## É preciso selecionar primeiro um profile.")
                input("Pressione Enter para continuar...")
                continue

            if vpc_id == '':
                print("## Nenhuma VPC selecionada. ")
                print("## É preciso selecionar primeiro uma VPC.")
                input("Pressione Enter para continuar...")
                continue

            valid = create_rds_submenu()
            while not valid:
                valid = create_rds_submenu()

        elif choice == "6":
            print("Saindo do programa...")
            break
        else:
            input("Opção inválida! Pressione Enter para continuar...")

        # if choice == '2':
        # 1    break


if __name__ == "__main__":
    main()


