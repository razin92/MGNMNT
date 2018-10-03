from django.shortcuts import render, HttpResponseRedirect, reverse
from info.models import Switch
from . import scripts
from .auth_data import login, password
import paramiko, datetime, time

def PortDown(request):
    scripts.SetPortStatus('192.168.1.3','TESTwr','1.3.6.1.2.2.1.7.2',2)
    return HttpResponseRedirect(reverse('info:switch_list'))

def base_connector(ip):
    client = paramiko.SSHClient()
    # получаем ключи SSH автоматически
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # данные для подключения
    try:
        client.connect(hostname=ip, username=login, password=password,
                       look_for_keys=False, allow_agent=False)

        # вызов командной строки, вывод данных(для исключения лишних)
        ssh = client.invoke_shell()
        time.sleep(0.4)
        ssh.recv(1000)
        return ssh
    except:
        return False

def SSH_connection(ip, port):
    # template = 'connector/ssh.html'
    # вызов клиента
    ssh = base_connector(ip)
    # команды и результаты вывода
    commands = ['sh vlan port %s' % port, 'sh fdb port %s' % port, 'sh error port %s' % port]
    result = []
    # выполнение команд
    for command in commands:
        ssh.send('\n%s\n' % command)
        time.sleep(0.4)
        out = ssh.recv(5000).decode('utf-8') or 'error'
        result.append(out.split('\n\r'))

    ssh.send('q\n')
    ssh.send('logout\n')

    fdb_header = ['VID', 'VLAN Name', 'MAC address', 'Port', 'Type', 'Status']
    fdb = [''.join([result[1][x]]).split() for x in range(6, result[1].index('', 6))]
    vlan_header = ['Port', 'VID', 'Untagged', 'Tagged', 'Dynamic', 'Forbidden']
    vlan = [''.join([result[0][x]]).split() for x in range(6, result[0].index('', 6))]
    error_source = ''.join(result[2][8:15]).split()

    error = [
        {'name': ' '.join(error_source[:2]), 'counter': error_source[2], 'type': 'rx_error'},
        {'name': error_source[6], 'counter': error_source[7], 'type': 'rx_error'},
        {'name': error_source[11], 'counter': error_source[12], 'type': 'rx_error'},
        {'name': error_source[16], 'counter': error_source[17], 'type': 'rx_error'},
        {'name': error_source[21], 'counter': error_source[22], 'type': 'rx_error'},
        {'name': ' '.join(error_source[26:28]), 'counter': error_source[28], 'type': 'rx_error'},
        {'name': ' '.join(error_source[31:33]), 'counter': error_source[33], 'type': 'rx_error'},
        {'name': ' '.join(error_source[3:5]), 'counter': error_source[5], 'type': 'tx_error'},
        {'name': ' '.join(error_source[8:10]), 'counter': error_source[10], 'type': 'tx_error'},
        {'name': ' '.join(error_source[13:15]), 'counter': error_source[15], 'type': 'tx_error'},
        {'name': ' '.join(error_source[18:20]), 'counter': error_source[20], 'type': 'tx_error'},
        {'name': ' '.join(error_source[23:25]), 'counter': error_source[25], 'type': 'tx_error'},
        {'name': error_source[29], 'counter': error_source[30], 'type': 'tx_error'}
    ]

    context = {
        'vlan_header': vlan_header,
        'vlan': vlan,
        'fdb_header': fdb_header,
        'fdb': fdb,
        'error': error,
    }

    return context

def backup_cfg():
    switches = Switch.objects.all()
    today = datetime.date.today()
    print('###START###')
    for each in switches:
        ip = each.ip_add
        print('Connecting to ', ip)
        ssh = base_connector(ip)
        if ssh is not False:
            command = 'upload cfg_toTFTP 192.168.220.200 dest_file %s_%s.cfg' % (ip, today)
            ssh.send('\n%s\n' % command)
            print('success!')
        else:
            print('fail!')
    print('###END OF THE OPERATION###')