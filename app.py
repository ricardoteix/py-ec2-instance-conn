import os
import subprocess
import sys
import time

import boto3

from src.credentials import get_active_credentials

selected_profile = ''
os.environ['ec2-conn-profile'] = selected_profile
connected = False


def describe_instances(profile: str):
    session = boto3.Session(profile_name=profile)
    ec2_client = session.client('ec2')
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                ]
            },
        ]
    )

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(
                {
                    'id': instance['InstanceId'],
                    'tags': instance['Tags'] if 'Tags' in instance else '',
                    'key_name': instance['KeyName'] if 'KeyName' in instance else '',
                    'vpc_id': instance['VpcId'],
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

    instance_id = instance['id']
    key_name = instance['key_name']
    vpc_id = instance['vpc_id']

    print("> Estabelecendo conexão SSH. Aguarde...")
    return f'aws ec2-instance-connect ssh --instance-id {instance_id} --os-user ubuntu --profile {selected_profile}'


def list_instances(new_menu):
    global selected_profile

    print("> Listando instâncias. Aguarde...")
    instances = describe_instances(selected_profile)

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

            print(f"{index + 1}. {instance['id']} ({instance_name})")
            options += f"{index + 1}"

        print(f"{len(instances) + 1}. Voltar ao menu anterior")

        options += f"{len(instances) + 1}"

        choice = input("Escolha uma opção: ")
        if choice not in options:
            print("-- Opção inválida. Selecione uma das opções possíveis.")
            time.sleep(3)
            return False

        selected_index = int(choice)

        for index, instance in enumerate(instances):
            if selected_index - 1 == index:
                return instance

        if selected_index == len(instances) + 1:
            print("Voltando...")

        return True


def create_credentials_submenu():
    global selected_profile

    selected_profile = ''
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
    open_terminal(tunel_command)

    print("> Solicitando informações para libera o acesso do RDS:")
    rds_endpoint = input("Host do RDS: ")
    local_port = input("Porta local do RDS: ")
    remote_port = input("Porta remota do RDS: ")
    ec2_key = input(f"Caminho da key da instância ({key_name}): ")
    os_user = input(f"Usuário do SO remoto (ubuntu ou ec2-user): ")

    rds_endpoint = rds_endpoint.encode(encoding='UTF-8', errors='strict').decode('utf8')

    if ec2_key == '':
        ec2_key = 'G:/Meu Drive/TI/AWS/chaves/mmm-dev.pem'

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
    while True:
        clear_screen()
        if selected_profile == '':
            print("[ Nenhum profile selecionado ]")
        else:
            print(f"[ Profile selecionado: {selected_profile} ]")

        print("Menu de Opções:\n")
        print("1. Selecionar Profile")
        print("2. Conectar à instância")
        print("3. Liberar acesso para RDS")
        print("4. Sair")

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

            valid = create_instances_submenu()
            while not valid:
                valid = create_instances_submenu()

            open_terminal(valid)

            # if connected:
            #     break

        elif choice == "3":

            if selected_profile == '':
                print("## Nenhum profile selecionado. ")
                print("## É preciso selecionar primeiro um profile.")
                input("Pressione Enter para continuar...")
                continue

            valid = create_rds_submenu()
            while not valid:
                valid = create_rds_submenu()

        elif choice == "4":
            print("Saindo do programa...")
            break
        else:
            input("Opção inválida! Pressione Enter para continuar...")

        # if choice == '2':
        # 1    break


if __name__ == "__main__":
    main()


