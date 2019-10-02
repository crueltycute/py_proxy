from socket import gethostname
from OpenSSL import crypto

CA_KEY_FILE = 'ca.key'
CA_FILE = 'ca.crt'


class CertificateAuthority:
    def __init__(self, ca_key_file=CA_KEY_FILE, ca_file=CA_FILE):
        self.ca_key_file = ca_key_file
        self.ca_file = ca_file
        self._generate_ca()

    def _generate_ca(self):
        # Generate key
        # create a key pair
        self.key = crypto.PKey()
        self.key.generate_key(crypto.TYPE_RSA, 2048)

        # Generate certificate
        self.cert = crypto.X509()
        self.cert.set_version(3)
        self.cert.set_serial_number(1)
        self.cert.get_subject().CN = '0.0.0.0'
        self.cert.gmtime_adj_notBefore(0)
        self.cert.gmtime_adj_notAfter(315360000)
        self.cert.set_issuer(self.cert.get_subject())
        self.cert.set_pubkey(self.key)
        self.cert.add_extensions([
            crypto.X509Extension(b'basicConstraints', True, b'CA:TRUE, pathlen:0'),
            crypto.X509Extension(b'keyUsage', True, b'keyCertSign, cRLSign'),
            crypto.X509Extension(b'subjectKeyIdentifier', False, b'hash', subject=self.cert),
        ])
        self.cert.sign(self.key, 'sha1')

        with open(self.ca_key_file, 'wb+') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, self.key))

        with open(self.ca_file, 'wb+') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, self.cert))
