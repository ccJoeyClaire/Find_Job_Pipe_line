# ssh 连接配置

## 1. windows 端配置 （powershell)

用户：```airflow_worker```

密码：```Airflow@123```

```powershell
#新建用户
New-LocalUser -Name "airflow_worker" -Password (ConvertTo-SecureString "Airflow@123" -AsPlainText -Force)

#查看用户配置
Get-LocalUser -Name "airflow_worker"

#设置新密码
Set-LocalUser -Name "airflow_worker" -Password (ConvertTo-SecureString "新密码" -AsPlainText -Force)
```



## 2. 容器内配置

##### 进入容器内 bash

容器名称： ```find_job_pipe_line_v2-airflow-scheduler-1```

```powershell
docker exec -it find_job_pipe_line_v2-airflow-scheduler-1 bash
```



##### 首先找到主机的 ipv4 地址:

```cmd
# cmd 输入
ipconfig

# 应当看到其中一项配置输出为
IPv4 地址 . . . . . . . . . . . . : 192.168.10.109
```



##### 在容器内：

```bash
# 在容器内添加SSH连接
airflow connections add 'windows_ssh' \
    --conn-type 'ssh' \
    --conn-host '192.168.10.109' \
    --conn-login 'airflow_worker' \
    --conn-password 'Airflow@123' \
    --conn-port 22


# 测试连接
ssh airflow_worker@192.168.10.109 "hostname && whoami"
# 应当输出 PCofPrincess(主机名称)与 pcofprincess\airflow_worker (主机名称/用户名称)

# 测试完整执行（包含目录切换）
ssh airflow_worker@192.168.10.109 "cd /d \"C:\\Users\\JoeyC\\Desktop\\Find_Job_Pipe_Line_V2\" && python dags\\test.py"

# 查看所有连接
airflow connections list

# 导出连接备份
airflow connections export connections.json

# 删除连接
airflow connections delete windows_ssh
```

