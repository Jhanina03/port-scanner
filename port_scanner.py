import socket
import re
import ipaddress
from common_ports import ports_and_services


def es_formato_ip(texto):
    """True si el texto parece una IP (solo numeros y puntos)."""
    return re.fullmatch(r'[\d.]+', texto) is not None


def get_open_ports(target, port_range, verbose=False):
    open_ports = []

    # 1. Validar el objetivo y obtener su IP
    if es_formato_ip(target):
        try:
            ipaddress.ip_address(target)  # ej: 266.255.9.10 no es valida
        except ValueError:
            return "Error: Invalid IP address"
        ip = target
    else:
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            return "Error: Invalid hostname"

    # 2. Revisar cada puerto del rango (incluye el ultimo)
    for port in range(port_range[0], port_range[1] + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex((ip, port)) == 0:  # 0 = conexion exitosa = puerto abierto
            open_ports.append(port)
        s.close()

    if not verbose:
        return open_ports

    # 3. Modo verbose: armar el texto descriptivo
    if es_formato_ip(target):
        try:
            hostname = socket.gethostbyaddr(ip)[0]  # DNS inverso
        except (socket.herror, socket.gaierror):
            hostname = None
    else:
        hostname = target

    if hostname:
        encabezado = f"Open ports for {hostname} ({ip})"
    else:
        encabezado = f"Open ports for {ip}"

    lineas = [encabezado, "PORT     SERVICE"]
    for port in open_ports:
        servicio = ports_and_services.get(port, "")
        lineas.append(f"{port:<9}{servicio}")

    return "\n".join(lineas)
