import subprocess

def install_docker_centos9():
    print("Installing Docker on CentOS 9...")
    cmds = [
        "sudo dnf -y remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine || true",
        "sudo dnf -y install dnf-plugins-core",
        "sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
        "sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
        "sudo systemctl enable docker",
        "sudo systemctl start docker"
    ]
    for cmd in cmds:
        subprocess.run(cmd, shell=True, check=True)

def deploy_container(uname="server_agent_v16", deployment_port=21026):
    image_name = f"tarunplotch/{uname}:latest"
    print(f"Pulling image: {image_name}")
    subprocess.run(["sudo", "docker", "pull", image_name], check=True)

    container_name = f"{uname}_container"
    print(f"Running container: {container_name}")
    run_cmd = [
        "sudo", "docker", "run", "-d",
        "--name", container_name,
        "-p", f"{deployment_port}:{deployment_port}",
        "-v", "/etc/groclake/auth:/etc/groclake/auth:ro",
        image_name,
        "sh", "-c",
        f"gunicorn --workers 1 --worker-class eventlet --worker-connections 80 -b 0.0.0.0:{deployment_port} groclake_server_agent:app"
    ]
    subprocess.run(run_cmd, check=True)

    ps_cmd = ["sudo", "docker", "ps", "--filter", f"name={container_name}", "--filter", "status=running", "--format", "{{.Names}}"]
    ps_proc = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
    running = ps_proc.stdout.strip().splitlines()

    if container_name in running:
        print(f"Container '{container_name}' is running.")
    else:
        raise RuntimeError(" Container failed to start.")

def full_deploy():
    install_docker_centos9()
    deploy_container()

