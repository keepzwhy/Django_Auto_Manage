from django.shortcuts import render, redirect
from app01 import models
from app01.utils.form import LogonModelForm, EditModelForm, LoginModelForm, ChangePasswordForm
from app01.utils.config import SERVER_IP, USERNAME, PASSWORD
import paramiko
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.safestring import mark_safe

# Create your views here.
# 用户登录
def login(request):
    if request.method == 'GET':
        form = LoginModelForm
        return render(request, 'login.html', {'form': form})

    form = LoginModelForm(data=request.POST)
    if form.is_valid():
        # 验证成功获取的用户名和密码
        username = form.cleaned_data['user_name']
        password = form.cleaned_data['user_password']

        user = models.UserInfo.objects.filter(user_name=username, user_password=password).first()
        if not user:
            form.add_error("user_password", "用户名或密码错误")
            return render(request, 'login.html', {'form': form})
        # 用户名密码正确
        # 将用户名写入session
        request.session["info"] = {'name': user.user_name}
        return redirect('/show/after/')
    return render(request, 'login.html', {'form': form})


# 注册
def logon(request):
    if request.method == 'GET':
        form = LogonModelForm
        return render(request, 'logon.html', {'form': form})
    # 数据校验
    form = LogonModelForm(data=request.POST)
    if form.is_valid():
        # 如果数据合法保存到数据库
        form.save()
        return redirect('/show/after/')
    return render(request, 'logon.html', {'form': form})


# 当前用户资料
def user_info(request):
    if request.method == 'GET':
        username = request.session.get("info", {}).get("name")
        user_info = models.UserInfo.objects.filter(user_name=username).first()
        return render(request, 'user_info.html', {'info': [user_info]})


# 修改当前用户资料
def user_edit(request, username):
    user_info = models.UserInfo.objects.filter(user_name=username).first()

    if request.method == 'POST':
        form = EditModelForm(request.POST, instance=user_info)
        if form.is_valid():
            form.save()
            return redirect('/show/after/')
    else:
        form = EditModelForm(instance=user_info)

    return render(request, 'user_edit.html', {'form': form})


# 服务器用户管理
def user_manage(request):
    if request.method == 'GET':
        server_ip = SERVER_IP
        username = USERNAME
        password = PASSWORD
        # 创建SSH客户端
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到服务器
        client.connect(server_ip, username=username, password=password)

        # 执行命令并获取信息
        command = "getent passwd | awk -F: '$3 >= 1000 {print $1}'"
        stdin, stdout, stderr = client.exec_command(command)
        users = stdout.read().decode().strip().split('\n')

        users_groups = []
        for user in users:
            group_command = f"groups {user} | awk -F: '{{print $2}}'"
            group_stdin, group_stdout, group_stderr = client.exec_command(group_command)
            groups = group_stdout.read().decode().strip().split(' ')
            users_groups.append({'user': user, 'groups': groups})
        # 关闭SSH连接
        client.close()
        return render(request, 'user_manage.html', {'users_groups': users_groups})


# 连接服务器获取信息
def service_info(request):
    server_ip = SERVER_IP
    username = USERNAME
    password = PASSWORD
    # 创建SSH客户端
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接到服务器
    client.connect(server_ip, username=username, password=password)
    # 执行命令并获取信息
    commands = [
        "hostname -I",  # 获取IP地址
        "cat /proc/cpuinfo | grep 'model name' | head -n 1 | awk -F ': ' '{print $2}'",  # 获取CPU信息
        "free -h | awk '/Mem/ {print $2}'",  # 获取内存信息
        "df -h --total | awk '/total/ {print $2}'"  # 获取存储信息
    ]
    server_info = []
    for command in commands:
        stdin, stdout, stderr = client.exec_command(command)
        info = stdout.read().decode().strip()
        server_info.append(info)
    # 关闭SSH连接
    client.close()
    return render(request, 'server_info.html', {'server_info': server_info})


# 用户修改密码
def change_pwd(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            input_name = form.cleaned_data['user_name']
            new_pwd = form.cleaned_data['user_password']

            user = models.UserInfo.objects.filter(user_name=input_name).first()
            if user:
                user.user_password = new_pwd
                user.save()
                return redirect('/login/')
            else:
                context = {
                    'form': form,
                    'error_message': '用户名输入错误',
                }
                return render(request, 'change_pwd.html', context)
    else:
        form = ChangePasswordForm()

    context = {
        'form': form,
    }
    return render(request, 'change_pwd.html', context)

# 登入后界面
def show_after(request):
    if request.method == 'GET':
        # 连接服务器
        server_ip = SERVER_IP
        username = USERNAME
        password = PASSWORD
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server_ip, username=username, password=password)
        # 获取内存信息
        stdin, stdout, stderr = client.exec_command('free -m')
        output = stdout.read().decode('utf-8')
        # 解析内存信息
        lines = output.strip().split('\n')
        headers = lines[0].split()
        mem = lines[1].split()
        swap = lines[2].split()
        # 已使用内存
        used_mem_head = headers[1]
        used_mem = int(mem[1])
        # 可用内存
        available_mem_head = headers[5]
        available_mem = int(mem[6])
        # 缓存
        buff_mem_head = headers[4]
        buff_mem = int(mem[5])
        # Swap
        swap_total = int(swap[1])
        swap_free = int(swap[3])
        db_data_list = [
            {"value": used_mem, "name": used_mem_head},
            {"value": available_mem, "name": available_mem_head},
            {"value": buff_mem, "name": buff_mem_head},
            {"value": swap_total, "name": "swap_total"},
            {"value": swap_free, "name": "swap_free"},
        ]
        db_data_json = json.dumps(db_data_list)
        # 获取磁盘信息
        stdin, stdout, stderr = client.exec_command('df -m')
        output1 = stdout.read().decode('utf-8')
        # 解析内存信息
        lines1 = output1.strip().split('\n')[1:]
        disk_usage = []
        for line in lines1:
            data = line.split()
            used_percent = data[4].replace('%', '')
            mount_point = data[5]
            disk_usage.append((used_percent, mount_point))
        db_data_list1 = [
            {"value": disk_usage[0][0], "name": disk_usage[0][1]},
            {"value": disk_usage[1][0], "name": disk_usage[1][1]},
            {"value": disk_usage[2][0], "name": disk_usage[2][1]},
            {"value": disk_usage[3][0], "name": disk_usage[3][1]},
            {"value": disk_usage[4][0], "name": disk_usage[4][1]},
            {"value": disk_usage[5][0], "name": disk_usage[5][1]},
            {"value": disk_usage[6][0], "name": disk_usage[6][1]},
        ]
        db_data_json1 = json.dumps(db_data_list1)
        # 获取服务器在线用户
        stdin, stdout, stderr = client.exec_command('who|wc -l')
        output2 = stdout.read().decode('utf-8')
        stdin, stdout, stderr = client.exec_command('ps -ef|wc -l')
        output3 = stdout.read().decode('utf-8')
        # 关闭连接
        client.close()
        return render(request, 'show_after.html',
                      {'db_data_json': db_data_json, 'db_data_json1': db_data_json1, 'online_users': output2,
                       'process': output3})


# 注销
def logout(request):
    request.session.clear()
    return redirect('/login/')


# 服务器用户管理
def service_user_edit(request, name):
    if request.method == 'GET':
        server_ip = SERVER_IP
        username = USERNAME
        password = PASSWORD
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server_ip, username=username, password=password)

        # 执行命令获取指定用户的组信息
        group_command = f"groups {name} | awk -F: '{{print $2}}'"
        group_stdin, group_stdout, group_stderr = client.exec_command(group_command)
        groups = group_stdout.read().decode().strip().split(' ')
        client.close()

        return render(request, 'service_user_edit.html', {'name': name, 'groups': groups})
    group = request.POST.get('group')
    # 连接服务器
    server_ip = SERVER_IP
    username = USERNAME
    password = PASSWORD
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server_ip, username=username, password=password)
    # 检查用户输入的所属组在服务器是否存在
    check_group_command = f"getent group {group}"
    check_group_stdin, check_group_stdout, check_group_stderr = client.exec_command(check_group_command)
    check_group_output = check_group_stdout.read().decode().strip()

    if not check_group_output:
        # 返回错误信息给前端，继续渲染编辑页面
        group_command = f"groups {name} | awk -F: '{{print $2}}'"
        group_stdin, group_stdout, group_stderr = client.exec_command(group_command)
        groups = group_stdout.read().decode().strip().split(' ')
        client.close()
        return render(request, 'service_user_edit.html', {'name': name, 'groups': groups, 'message': '所属组不存在'})
    # 执行修改所属组的命令
    group_command = f"sudo usermod -g {group} {name}"
    stdin, stdout, stderr = client.exec_command(group_command)
    group_output = stdout.read().decode()

    client.close()

    return redirect('/user/manager/')  # 重定向到用户列表页面或其他适当的页面


@csrf_exempt
# 服务器用户编辑
def new_built_user(request):
    if request.method == 'GET':
        return render(request, 'new_built_user.html')
    # 获取前端输入的信息
    name = request.POST.get("name")
    group = request.POST.get("group")
    user_password = request.POST.get("password")
    delete_name = request.POST.get("user_group.user")
    # 连接服务器
    server_ip = SERVER_IP
    username = USERNAME
    password = PASSWORD
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server_ip, username=username, password=password)
    # 检查用户输入的所属组在服务器是否存在
    check_group_command = f"getent group {group}"
    check_group_stdin, check_group_stdout, check_group_stderr = client.exec_command(check_group_command)
    check_group_output = check_group_stdout.read().decode().strip()
    if not check_group_output:
        # 创建所属组
        create_group_command = f"sudo groupadd {group}"
        stdin, stdout, stderr = client.exec_command(create_group_command)
        create_group_output = stdout.read().decode()
        if stderr.channel.recv_exit_status() != 0:
            client.close()
            return render(request, 'new_built_user.html', {'name': name, 'message': '无法创建新的所属组'})
    # 执行添加用户和其所在所属组
    user_add = f"sudo useradd -g {group} {name}"
    stdin, stdout, stderr = client.exec_command(user_add)
    user_add_output = stdout.read().decode()
    # 删除用户
    if delete_name:
        delete_command = f"sudo userdel {delete_name} && sudo rm -rf /home/{delete_name} && sudo rm -rf /var/mail/{delete_name}"
        stdin, stdout, stderr = client.exec_command(delete_command)
        delete_command_output = stdout.read().decode()
    # 用户密码
    user_password_command = f"echo '{user_password}'|passwd --stdin {name} > /dev/null 2>&1"
    user_password_stdin, user_password_stdout, user_password_stderr = client.exec_command(user_password_command)
    user_password_output = user_password_stdout.read().decode()
    client.close()
    return redirect('/user/manager/')


# cpu动态监控
def monitor_cpu(request):
    return render(request, 'monitor_cpu.html')


# 内存动态监控
def monitor_mem(request):
    return render(request, 'monitor_mem.html')


# 进程管理
def process_manager(request):
    # 连接服务器
    server_ip = SERVER_IP
    username = USERNAME
    password = PASSWORD
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server_ip, username=username, password=password)
    # 执行命令获取进程的信息
    process_comm = f"ps aux | tail -n +2"
    group_stdin, group_stdout, group_stderr = client.exec_command(process_comm)
    process_list_output = group_stdout.read().decode()
    # 处理进程信息并放入列表
    processes = process_list_output.splitlines()
    process_info_list = []
    for process in processes:
        process_info = process.split()
        command_part = ' '.join(process_info[10:])  # 将第十一列之后的部分用空格连接起来
        del process_info[10:]  # 删除原来的第十一列之后的内容
        process_info.append(command_part)  # 添加整合后的命令部分作为新的最后一列
        process_info_list.append(process_info)
    # 分页
    total_count = len(process_info_list) - 1
    page = int(request.GET.get('page', 1))
    page_size = 8
    start = (page - 1) * page_size
    end = page * page_size
    pro_list = process_info_list[start:end]
    # 总页码
    total_page_count, div = divmod(total_count, page_size)
    if div:
        total_page_count += 1
    plus = 3
    # 判断当前页小于3
    if page <= 3:
        start_page = 1
        end_page = 2 * plus + +1
    else:
        # 当前页大于3
        if (page + plus) > total_page_count:
            start_page = total_page_count - 2 * plus
            end_page = total_page_count
        else:
            # 只显示当前页的前3页和后3页
            start_page = page - plus
            end_page = page + plus
    page_str_list = []
    # 上一页
    if page > 1:
        pre = '<li><a href="?page={}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(
            page - 1)
    else:
        pre = '<li><a href="?page={}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(1)
    page_str_list.append(pre)

    for i in range(start_page, end_page + 1):
        if i == page:
            li = '<li class="active"><a href="?page={}">{}</a></li>'.format(i, i)
        else:
            li = '<li><a href="?page={}">{}</a></li>'.format(i, i)
        page_str_list.append(li)
    # 下一页
    if page < total_page_count:
        pre = '<li><a href="?page={}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(
            page + 1)
    else:
        pre = '<li><a href="?page={}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(
            total_page_count)
    page_str_list.append(pre)
    page_string = mark_safe("".join(page_str_list))
    # 搜索
    value = request.GET.get('q')
    filtered_list = []
    if value:
        filtered_list = [item for item in process_info_list if
                         item is not None and any(value in sub_item for sub_item in item)]
    context = {'filtered_list': filtered_list}
    client.close()
    return render(request, 'process_manager.html',
                  {'process_info_list': pro_list, 'page_string': page_string, 'value': value, **context})
