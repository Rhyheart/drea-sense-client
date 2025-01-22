import datetime
import ipaddress
import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from app.cores.config import config

class CertService:
    def __init__(self):
        self.cert_dir = "app/certs"
        self.validity_days = 18250
        
    def generate_cert(self):
        """生成SSL证书和私钥"""
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # 准备证书主题和颁发者信息
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])

        # 准备证书
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=self.validity_days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1"))
            ]),
            critical=False
        ).sign(private_key, hashes.SHA256())

        # 创建证书目录
        os.makedirs(self.cert_dir, exist_ok=True)

        # 保存证书和私钥
        cert_path = os.path.join(self.cert_dir, "cert.pem")
        key_path = os.path.join(self.cert_dir, "key.pem")
        
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

    def init_ssl_cert(self):
        """初始化SSL证书"""
        cert_path = os.path.join(self.cert_dir, "cert.pem")
        key_path = os.path.join(self.cert_dir, "key.pem")
        
        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            self.generate_cert()
        return (cert_path, key_path)

# 创建全局证书服务实例
cert_service = CertService() 